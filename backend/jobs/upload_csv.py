import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from django.core.exceptions import ValidationError

import csv

from django.db import transaction

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.local")
# django.setup()

from api.models import Holding, User, Account, Investment, UserHolding
from backend.settings.base import TIME_ZONE

dir_path = os.path.dirname(os.path.realpath(__file__))

CSV_ACCOUNT_ASSET = os.path.join(dir_path, "csv/account_asset_info_set.csv")
CSV_ACCOUNT_BASIC = os.path.join(dir_path, "csv/account_basic_info_set.csv")
CSV_ASSET_GROUP = os.path.join(dir_path, "csv/asset_group_info_set.csv")


def upload_asset_group_info(csv_asset_group):
    """
    자산군 그룹 상세 CSV File Upload
    :param csv_asset_group:
    :return:
    """
    with open(csv_asset_group) as in_file:
        data_reader = csv.reader(in_file)
        result = {
            "total_csv_rows": 0,
            "success_rows": 0,
            "failed_rows": 0,
            "invalid_rows": [],
        }
        for idx, row in enumerate(data_reader):
            # 헤더는 건너뜀
            if idx == 0:
                continue

            try:
                stock_name, ISIN, asset_group_name = row[0], row[1], row[2]

                # 중복되지 않은 자산군인 데이터만 생성
                if not (stock_name and ISIN and asset_group_name):
                    raise KeyError("row 데이터가 충분치 않습니다.")

                if Holding.objects.filter(name=stock_name):
                    raise ValidationError("중복된 종목명이 존재합니다.")

                if Holding.objects.filter(isin=ISIN):
                    raise ValidationError("중복된 ISIN이 존재합니다.")

                Holding.objects.create(
                    name=stock_name, isin=ISIN, asset_group=asset_group_name
                )
                result["success_rows"] += 1

            except Exception as e:
                # raise ValidationError(str(e))
                result["failed_rows"] += 1
                result["invalid_rows"].append(
                    {"error row": idx + 1, "error detail": str(e)}
                )
                continue

            result["total_csv_rows"] += 1

        return result


def upload_asset_info(csv_asset_info):
    """
    자산 상세 CSV File Upload
    :param csv_asset_info:
    :param csv_asset_basic_info:
    :return:
    """
    with open(csv_asset_info) as in_file:
        data_reader = csv.reader(in_file)
        result = {
            "total_csv_rows": 0,
            "success_rows": 0,
            "failed_rows": 0,
            "invalid_rows": [],
        }
        for idx, row in enumerate(data_reader):
            # 헤더는 건너뜀
            if idx == 0:
                continue

            try:
                (
                    user_name,
                    brokerage,
                    account_number,
                    account_name,
                    ISIN,
                    current_price,
                    holding_quantity,
                ) = (row[0], row[1], row[2], row[3], row[4], row[5], row[6])

                if not (
                    user_name
                    and brokerage
                    and account_number
                    and account_name
                    and current_price
                    and holding_quantity
                ):
                    raise ValidationError("row 데이터가 충분치 않습니다.")

                holding = Holding.objects.get(isin=ISIN)
                holding.current_price = current_price
                holding.save()

                account = Account.objects.get_or_create(
                    account_name=account_name,
                    account_number=account_number,
                )[0]

                user = User.objects.get_or_create(account=account, name=user_name)[0]
                investment = Investment.objects.get_or_create(
                    user=user, brokerage=brokerage
                )[0]

                user_holding = UserHolding.objects.get_or_create(
                    holding=holding, user=user
                )[0]
                user_holding.quantity = holding_quantity
                user_holding.current_price = current_price
                user_holding.save()

                result["success_rows"] += 1

            except Exception as e:
                result["failed_rows"] += 1
                result["invalid_rows"].append(
                    {"error row": idx + 1, "error detail": str(e)}
                )
                continue

            result["total_csv_rows"] += 1

        return result


def upload_asset_basic(csv_asset_basic):
    """
    기본 자산 CSV File Upload
    :param csv_asset_basic:
    :return:
    """
    with open(csv_asset_basic) as in_file:
        data_reader = csv.reader(in_file)
        result = {
            "total_csv_rows": 0,
            "success_rows": 0,
            "failed_rows": 0,
            "invalid_rows": [],
        }

        for idx, row in enumerate(data_reader):
            # 헤더는 건너뜀
            if idx == 0:
                continue

            try:
                account_number, principal = row[0], row[1]
                if not (account_number and principal):
                    raise ValidationError("row 데이터가 충분치 않습니다.")

                account = Account.objects.get(account_number=account_number)
                investment = account.user.investment
                investment.principal = principal
                investment.save()

                result["success_rows"] += 1

            except Exception as e:
                result["failed_rows"] += 1
                result["invalid_rows"].append(
                    {"error row": idx + 1, "error detail": str(e)}
                )
                continue

            result["total_csv_rows"] += 1
        return result


@transaction.atomic
def calculate_account_total_asset():
    try:
        users = User.objects.all()
        for user in users:
            user_account = user.account
            user_account.total_assets = 0

            for user_holding in user.user_holdings.all():
                user_account.total_assets += (
                    user_holding.current_price * user_holding.quantity
                )

            user_account.save()

    except Exception as e:
        transaction.set_rollback(rollback=True)
        raise ValidationError(str(e))


def execute_csv_uploader():
    """
    Execute all csv uploader function
    :return:
    """
    filename = os.path.join(dir_path, "../csv_uploader_log.log")

    # Logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)
    logger.info("csv upload start..")

    upload_asset_group_info(CSV_ASSET_GROUP)
    upload_asset_info(CSV_ACCOUNT_ASSET)
    upload_asset_basic(CSV_ACCOUNT_BASIC)
    calculate_account_total_asset()

    logger.info("csv upload end..")


def start():
    """
    스케쥴러 실행
    - 실행 함수 : execute_csv_uploader
    - 주기 : 매일 06시 실행
    :return:
    """
    scheduler = BackgroundScheduler(timezone=TIME_ZONE)
    scheduler.add_job(
        execute_csv_uploader,
        id="execute_csv_uploader",
        trigger=CronTrigger(hour="6"),
        # trigger=CronTrigger(second="*/20"),
        max_instances=1,
        replace_existing=True,
        coalesce=True,
    )
    scheduler.start()

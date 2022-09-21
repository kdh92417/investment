from api.models import Investment


def calculate_total_proceeds(instance: Investment):
    """
    총 수익금 계산
    :param instance: Investment instance
    :return:
    """
    return instance.user.account.total_assets - instance.principal


def calculate_proceeds_rate(instance: Investment):
    """
    수익률 계산
    :param instance: Investment instance
    :return:
    """
    return round(
        (instance.user.account.total_assets - instance.principal)
        / (instance.principal * 100),
        4,
    )

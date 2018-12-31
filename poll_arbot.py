import os
import datetime
import logging
import pytz

from arbot_api import ArbotApi
from email_api import EmailApi

SES_USERNAME = os.environ.get('SES_USERNAME', None)
SES_PASSWORD = os.environ.get('SES_PASSWORD', None)
NOTIFICATION_EMAIL_TO = os.environ.get('NOTIFICATION_EMAIL_TO', None)
NOTIFICATION_EMAIL_FROM = os.environ.get('NOTIFICATION_EMAIL_FROM', None)
HOST = os.environ.get('HOST', None)
EMAIL = os.environ.get('EMAIL', None)
PASSWORD = os.environ.get('PASSWORD', None)
TOKEN = os.environ.get('TOKEN', None)
USER_ID = os.environ.get('USER_ID', None)
BOX_ID = os.environ.get('BOX_ID', None)
BOX_LOCATION = os.environ.get('BOX_LOCATION', None)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
arbot_api = ArbotApi(
    host=HOST,
    email=EMAIL,
    password=PASSWORD,
    token=TOKEN,
    user_id=USER_ID,
    box_id=BOX_ID,
    box_location=BOX_LOCATION
)
email_api = EmailApi(
    username=SES_USERNAME,
    password=SES_PASSWORD,
    to_email=NOTIFICATION_EMAIL_TO,
    from_email=NOTIFICATION_EMAIL_FROM
)


def poll_workouts(event, context):
    target_workouts = event.get('target_workouts', [])
    delta = event.get('delta', 72)
    max_delta = event.get('max_delta', 24)
    if not isinstance(target_workouts, (list,)):
        target_workouts = [target_workouts]

    min_date = _get_min_date(delta)
    max_date = _get_max_date(max_delta, min_date)
    schedules = arbot_api.get_schedule(datetime.datetime.strftime(min_date, '%Y-%m-%d'))
    filtered_schedules = _filter_schedules(schedules, target_workouts, min_date, max_date)
    if not filtered_schedules:
        logger.info('no workouts to sign up for')
        return {
            'statusCode': 200,
            'body': {'result': 'no workouts to sign up for'}
        }

    membership = arbot_api.get_membership()
    return {
        'statusCode': 200,
        'body': {'result': [_register_schedule(filtered_schedule, membership) for filtered_schedule in filtered_schedules]}
    }


def _get_min_date(delta):
    tz = pytz.timezone('Asia/Jerusalem')
    min_date = datetime.datetime.now(tz) + datetime.timedelta(hours=delta)
    return min_date


def _get_max_date(max_delta, min_date):
    max_date = min_date + datetime.timedelta(hours=max_delta)
    return max_date


def _filter_schedules(schedules, target_workouts, min_date, max_date):
    filtered = []
    for schedule in schedules:
        name = schedule.get('category', {}).get('name', None)
        if not name:
            logger.warning('not registering. could not find a workout name in schedule {}'.format(schedule))
            continue

        if name not in target_workouts:
            logger.info('not registering. schedule {} is not in workouts {}'.format(name, target_workouts))
            continue

        time = schedule.get('schedule', {}).get('time', None)
        date = schedule.get('schedule', {}).get('date', None)
        if not time:
            logger.warning('not registering. could not find a workout time in schedule {}'.format(schedule))
            continue

        schedule_time = datetime.datetime.strptime('{} {} +0200'.format(date, time), '%Y-%m-%d %H:%M:%S %z')
        if min_date < schedule_time:
            logger.info('not registering. schedule {} at {} is later than {}'.format(name, schedule_time, min_date))
            continue

        if schedule_time < max_date:
            logger.info('not registering. schedule {} at {} is earlier than {}'.format(name, schedule_time, min_date))
            continue

        already_member = schedule['alreadyMember']
        if already_member:
            logger.info('not registering. already signed up for schedule {} at {}'.format(name, schedule_time))
            continue

        filtered.append(schedule)

    return filtered


def _register_schedule(filtered_schedule, membership):
    logger.info('registering up for schedule {}'.format(filtered_schedule))
    try:
        result = arbot_api.register_for_workout(membership['id'], filtered_schedule['schedule']['id'])
        _handle_successful_registration(filtered_schedule, result)
    except Exception as e:
        logging.error(e)


def _handle_successful_registration(filtered_schedule, result):
    logger.info('succeeded to register with response {}'.format(result))
    _send_success_email(filtered_schedule, result)


def _send_success_email(filtered_schedule, result):
    name = filtered_schedule.get('category', {}).get('name', None)
    time = filtered_schedule.get('schedule', {}).get('time', None)
    date = filtered_schedule.get('schedule', {}).get('date', None)
    email_api.send_email(
        'ARBot',
        'ARBot signed up for workout {} at {} {}'.format(name, date, time),
        'please add {} to calendar at {} {}'.format(name, date, time)
    )


if __name__ == "__main__":
    poll_workouts({
        'target_workouts': ['יוגה'],
        'delta': 72,
        'max_delta': 1
    }, None)

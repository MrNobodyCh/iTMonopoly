from getters import DBGetter
from config import DBSettings

test_users = range(1, 1000)

for x in test_users:
    DBGetter(DBSettings.HOST).insert("INSERT INTO users (user_id, is_subscribed_to_courses, is_subscribed_to_events) "
                                     "VALUES (%s, TRUE, TRUE )" % int(x))
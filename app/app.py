import calendar
import datetime
import random
import string

from sqlalchemy import and_, func
from . import Report, db


def gen_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def tg_user_by_id(tg_id: int) -> db.TGUserModel:
    with db.Session() as session:
        return session.query(db.TGUserModel).filter(db.TGUserModel.tg_id == tg_id).first()


def user_by_token(token: str) -> db.UserModel:
    with db.Session() as session:
        return session.query(db.UserModel).filter(db.UserModel.utoken == token).first()


def user_by_id(_id: int) -> db.UserModel:
    with db.Session() as session:
        return session.query(db.UserModel).filter(db.UserModel.id == _id).first()


def all_users():
    with db.Session() as session:
        return session.query(db.UserModel).all()


def work_months():
    with db.Session() as session:
        for date in session.query(
                func.extract('year', db.WorkDayModel.day), func.extract('month', db.WorkDayModel.day)
        ).distinct():
            yield f"{date[1]}.{date[0]}"


def last_fix_time(user_id: int) -> db.UserTimeInModel | db.UserTimeOutModel | None:
    with db.Session() as session:
        last_user_time_in = (session.query(db.UserTimeInModel).filter(db.UserTimeInModel.user_id == user_id)
                             .order_by(db.UserTimeInModel.id.desc()).first())
        last_user_time_out = (session.query(db.UserTimeOutModel).filter(db.UserTimeOutModel.user_id == user_id)
                              .order_by(db.UserTimeOutModel.id.desc()).first())
        if last_user_time_in is None:
            return None
        elif last_user_time_out is None:
            return last_user_time_in
        else:
            return last_user_time_in if last_user_time_in.time > last_user_time_out.time else last_user_time_out


def reg_tg_user(token: str, tg_id: int) -> db.UserModel:
    with db.Session() as session:
        if (user := user_by_token(token)) is not None:
            tg_user = tg_user_by_id(tg_id) or db.TGUserModel()
            tg_user.user_id = user.id
            tg_user.tg_id = tg_id
            session.add(tg_user)
            session.commit()
            return user


def verificate_user(tg_id: int) -> db.UserModel:
    with db.Session() as session:
        if (tg_user := session.query(db.TGUserModel).filter(db.TGUserModel.tg_id == tg_id).first()) is not None:
            return tg_user.user


def verificate_admin(chat_id: int):
    with db.Session() as session:
        return session.query(db.TGAdminModel).filter(db.TGAdminModel.chat_id == chat_id).first() is not None


def fix_time(tg_id: int):
    with db.Session() as session:
        tg_user = tg_user_by_id(tg_id)
        if isinstance(last_fix_time_model := last_fix_time(tg_user.user_id), db.UserTimeInModel):
            fix_time_model = db.UserTimeOutModel(user_id=tg_user.user_id)
        else:
            fix_time_model = db.UserTimeInModel(user_id=tg_user.user_id)
        session.add(fix_time_model)

        if isinstance(last_fix_time_model, db.UserTimeInModel):
            if ((work_day := session.query(db.WorkDayModel).
                    filter(and_(db.WorkDayModel.day == last_fix_time_model.time.date(),
                                db.WorkDayModel.user_id == tg_user.user_id))
                    .first()) is None):
                work_day = db.WorkDayModel(user_id=tg_user.user_id, time=0)
            work_day.time += round((fix_time_model.time.timestamp() - last_fix_time_model.time.timestamp()) / 3600, 1)
            session.add(work_day)

        session.commit()
        session.refresh(fix_time_model)
        return fix_time_model


def get_user_hours(tg_id: int, month: int, year: int):
    with db.Session() as session:
        for work_day in (session.query(db.WorkDayModel).filter(and_(
                db.WorkDayModel.user_id == tg_user_by_id(tg_id).user_id,
                db.WorkDayModel.day >= datetime.date(year, month, 1),
                db.WorkDayModel.day < datetime.date(year if month < 12 else year + 1, month + 1 if month < 12 else 1, 1)
        )).order_by(db.WorkDayModel.day).all()):
            yield work_day


def create_admin_hours_report(month: int, year: int) -> str:
    data = {}
    with db.Session() as session:
        for model in (session.query(db.WorkDayModel).filter(and_(
                db.WorkDayModel.day >= datetime.date(year, month, 1),
                db.WorkDayModel.day < datetime.date(year if month < 12 else year + 1, month + 1 if month < 12 else 1, 1)
        )).all()):
            if data.get(model.user.name) is None:
                data[model.user.name] = {}
            data[model.user.name][model.day.day] = model.time if model.time - int(model.time) else int(model.time)

    report = Report(f"Отчет по рабочему времени сотрудников за {month}.{year}")
    report.add_h1(f"Отчет по рабочему времени сотрудников за {month}.{year}")

    first_half_monthrange = list(range(1, 16))
    second_half_monthrange = list(range(16, calendar.monthrange(year, month)[1] + 1))

    report.add_h2("Первая половина:")
    report.add_table(
        ['', *first_half_monthrange, 'Всего'],
        [[name] + [data[name][i] if data[name].get(i) else '' for i in first_half_monthrange] +
         [sum(data[name][i] for i in first_half_monthrange if data[name].get(i))] for name in data.keys()]
    )

    report.add_h2("Вторая половина:")
    report.add_table(
        ['', *second_half_monthrange, 'Всего', 'За месяц'],
        [[name] + [data[name][i] if data[name].get(i) else '' for i in second_half_monthrange] +
         [sum(data[name][i] for i in second_half_monthrange if data[name].get(i))] +
         [sum(data[name][i] for i in first_half_monthrange + second_half_monthrange if data[name].get(i))]
         for name in data.keys()]
    )

    return report.create_pdf()


def register_user(name: str):
    with db.Session() as session:
        while session.query(db.UserModel).filter(db.UserModel.utoken == (token := gen_token())).first() is not None:
            pass
        user = db.UserModel(name=name, utoken=token)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def remove_user(user_id: int) -> db.UserModel:
    with db.Session() as session:
        if (user := session.query(db.UserModel).filter(db.UserModel.id == user_id).first()) is not None:
            session.delete(user)
            session.commit()
            return user


def correctable_work_day(user_id: int):
    today = datetime.date.today()
    with db.Session() as session:
        for i in range(1, 15):
            if (work_day_model := session.query(db.WorkDayModel).filter(and_(
                    db.WorkDayModel.user_id == user_id,
                    db.WorkDayModel.day == (cur_data := today - datetime.timedelta(days=i))
            )).first()) is None:
                yield db.WorkDayModel(user_id=user_id, day=cur_data, time=0)
            else:
                yield work_day_model


def correct_day(user_id: int, day: datetime.date, new_time: float):
    with db.Session() as session:
        if (work_day := session.query(db.WorkDayModel).filter(
                and_(db.WorkDayModel.user_id == user_id, db.WorkDayModel.day == day)).first()) is not None:
            work_day.time = new_time
        else:
            session.add(db.WorkDayModel(user_id=user_id, day=day, time=new_time))
        session.commit()


def user_work_months(tg_id: int):
    tg_user = tg_user_by_id(tg_id)
    with db.Session() as session:
        for date in session.query(
                func.extract('year', db.WorkDayModel.day), func.extract('month', db.WorkDayModel.day)
        ).filter(db.WorkDayModel.user_id == tg_user.user_id).distinct():
            yield f"{date[1]}.{date[0]}"


def all_admins():
    with db.Session() as session:
        return session.query(db.TGAdminModel).all()


def is_new_tg_user(tg_id: int):
    with db.Session() as session:
        if session.query(db.TGUserModel).filter(db.TGUserModel.tg_id == tg_id).first() is None:
            session.add(db.TGUserModel(tg_id=tg_id))
            session.commit()
            return True
        else:
            return False

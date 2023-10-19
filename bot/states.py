from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationState(StatesGroup):
    """Машина состояний для регистрации пользователя."""
    start: State = State()


class NewBoxState(StatesGroup):
    """Машина состояний для добавления ящика."""
    domain: State = State()
    username: State = State()
    password: State = State()
    filters: State = State()
    filter_loop: State = State()
    approve: State = State()


class MyBoxesState(StatesGroup):
    """Машина состояний для проcмотра ящиков."""
    start: State = State()
    one_box: State = State()

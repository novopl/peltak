from peltak.core import exc


def test_can_use_root_exception_directly():
    ex = exc.PeltakError()
    assert str(ex) == "peltak error"

    ex = exc.PeltakError("detail")
    assert str(ex) == "peltak error: detail"


def test_can_easily_define_subclasses():
    class TestError(exc.PeltakError):
        msg = "Test Error"

    ex = TestError()
    assert str(ex) == "Test Error"

    ex = TestError("detail")
    assert str(ex) == "Test Error: detail"

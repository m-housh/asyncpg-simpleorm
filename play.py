#!/usr/bin/env python


class ColumnTypeMeta(type):

    def __new__(cls, name, bases, namespace, **kwargs):

        if '__slots__' not in namespace:
            if '__init__' in namespace:
                raise RuntimeError(
                    f'{name} does not declare __slots__, but has __init__'
                )
            namespace['__slots__'] = ()

        return type.__new__(cls, name, bases, namespace, **kwargs)


class ColumnType(metaclass=ColumnTypeMeta):

    __slots__ = ()

    @property
    def type_string(self):
        return getattr(self, '_type_string', None)

    def __init_subclass__(cls, type_string=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if not type_string:
            raise RuntimeError(
                f'ColumnType subclass did not declare type_string: {cls}'
            )
        cls._type_string = str(type_string)


class UUID(ColumnType, type_string='uuid'):
    pass


class Integer(ColumnType, type_string='integer'):
    pass


class Fail(ColumnType):
    pass


if __name__ == '__main__':

    print(UUID().type_string, hasattr(UUID(), '__dict__'))
    print(Integer().type_string)

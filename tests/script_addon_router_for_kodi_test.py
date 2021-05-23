from __future__ import annotations
import unittest
from unittest.mock import patch, MagicMock
import sys
import asyncio
from resources.lib.sakura import ScriptAddonRouterForKodi


class TestScriptAddonRouterForKodi(unittest.TestCase):

    def test_get_url_query_function_str(self):
        query = ScriptAddonRouterForKodi.get_url_query('function1')
        self.assertEqual(query, 'f=function1')

    def function2(self):
        pass

    def test_get_url_query_callable(self):
        query = ScriptAddonRouterForKodi.get_url_query(self.function2)
        self.assertEqual(query, 'f=function2')

    def test_get_url_query_arg_int(self):
        query = ScriptAddonRouterForKodi.get_url_query(self.function2, 123)
        self.assertEqual(query, 'f=function2&0=i123')

    def test_get_url_query_arg_float(self):
        query = ScriptAddonRouterForKodi.get_url_query(self.function2, 123.4)
        self.assertEqual(query, 'f=function2&0=f123.4')

    def test_get_url_query_arg_bool(self):
        query = ScriptAddonRouterForKodi.get_url_query(self.function2, True)
        self.assertEqual(query, 'f=function2&0=bTrue')

    def test_get_url_query_arg_str(self):
        query = ScriptAddonRouterForKodi.get_url_query(self.function2, "abc")
        self.assertEqual(query, 'f=function2&0=sabc')

    def test_get_url_query_args(self):
        query = ScriptAddonRouterForKodi.get_url_query(self.function2, 123, 123.4, True, "abc")
        self.assertEqual(query, 'f=function2&0=i123&1=f123.4&2=bTrue&3=sabc')

    def test_parse_url_query_function(self):
        query = 'f=function1'
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function1')
        self.assertEqual(args, [])

    def test_parse_url_query_arg_int(self):
        query = 'f=function1&0=i123'
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function1')
        self.assertEqual(args, [123])
        self.assertEqual(type(args[0]), int)

    def test_parse_url_query_arg_float(self):
        query = 'f=function1&0=f123.4'
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function1')
        self.assertEqual(args, [123.4])
        self.assertEqual(type(args[0]), float)

    def test_parse_url_query_arg_bool(self):
        query = 'f=function1&0=bTrue'
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function1')
        self.assertEqual(args, [True])
        self.assertEqual(type(args[0]), bool)

    def test_parse_url_query_arg_str(self):
        query = 'f=function1&0=sabc'
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function1')
        self.assertEqual(args, ['abc'])
        self.assertEqual(type(args[0]), str)

    def test_parse_url_query_args(self):
        query = 'f=function1&0=i123&1=f123.4&2=bTrue&3=sabc'
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function1')
        self.assertEqual(args, [123, 123.4, True, 'abc'])
        self.assertEqual(type(args[0]), int)
        self.assertEqual(type(args[1]), float)
        self.assertEqual(type(args[2]), bool)
        self.assertEqual(type(args[3]), str)

    def test_get_and_parse_url_query_arg_list(self):
        value = [123, 123.4, True, 'abc']
        query = ScriptAddonRouterForKodi.get_url_query(self.function2, value)
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function2')
        self.assertEqual(type(args[0]), type(value))
        self.assertEqual(args[0], value)

    def test_get_and_parse_url_query_arg_tuple(self):
        value = (123, 123.4, True, 'abc')
        query = ScriptAddonRouterForKodi.get_url_query(self.function2, value)
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function2')
        self.assertEqual(type(args[0]), type(value))
        self.assertEqual(args[0], value)

    def test_get_and_parse_url_query_arg_dict(self):
        value = {'key0': 123, 'elem1': 123.4, 'arg2': True, 'index3': 'abc'}
        query = ScriptAddonRouterForKodi.get_url_query(self.function2, value)
        func_str, args = ScriptAddonRouterForKodi.parse_url_query(query)
        self.assertEqual(func_str, 'function2')
        self.assertEqual(type(args[0]), type(value))
        self.assertEqual(args[0], value)

    async def test_entrance_call(self):
        sys_argv_mock = ['', 1, '']
        with patch.object(sys, 'argv', sys_argv_mock):
            test = ScriptAddonRouterForKodiTest()
            test.entrance = MagicMock()
            await test()
            test.entrance.assert_called_once()

    async def test_no_arg_function_call(self):
        sys_argv_mock = ['', 1, '?f=no_arg_function']
        with patch.object(sys, 'argv', sys_argv_mock):
            test = ScriptAddonRouterForKodiTest()
            with patch.object(test, 'no_arg_function', MagicMock()):
                await test()
                test.no_arg_function.assert_called_once()

    async def test_arg_function_call(self):
        sys_argv_mock = ['', 1, '?f=arg_function&0=f123.4']
        with patch.object(sys, 'argv', sys_argv_mock):
            test = ScriptAddonRouterForKodiTest()
            with patch.object(test, 'arg_function', MagicMock()):
                await test()
                test.arg_function.assert_called_once_with(123.4)

    async def test_async_function_call(self):
        sys_argv_mock = ['', 1, '?f=async_function']
        with patch.object(sys, 'argv', sys_argv_mock):
            test = ScriptAddonRouterForKodiTest()
            with patch.object(test, 'async_function_leaf', MagicMock()):
                await test()
                self.assertEqual(test.async_function_leaf.call_count, 4)


class ScriptAddonRouterForKodiTest(ScriptAddonRouterForKodi):
    def __init__(self):
        super(ScriptAddonRouterForKodiTest, self).__init__(self.entrance)

    def entrance(self) -> None:
        pass

    def no_arg_function(self) -> None:
        pass

    def arg_function(self, value) -> None:
        pass

    async def async_function(self) -> None:
        await self.async_function_nest()
        await asyncio.sleep(0.1)
        await self.async_function_nest()

    async def async_function_nest(self) -> None:
        self.async_function_leaf()
        await asyncio.sleep(0.1)
        self.async_function_leaf()
        await asyncio.sleep(0.1)

    def async_function_leaf(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()

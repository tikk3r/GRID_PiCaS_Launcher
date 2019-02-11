import unittest
from GRID_PiCaS_Launcher.picas.modifiers import TokenModifier
from GRID_PiCaS_Launcher.picas.modifiers import NestedTokenModifier


class testSandbox(unittest.TestCase):

    def test_timeout(self):
        t = TokenModifier()
        self.assertTrue(t.timeout == 86400)
        t = TokenModifier(1000)
        self.assertTrue(t.timeout == 1000)

    def test_Exceptions(self):
        t = TokenModifier()
        try:
           t.lock()
        except NotImplementedError as e:
            self.assertTrue(str(e)=='Lock function not implemented.')
        try:
            t.unlock()
        except NotImplementedError as e:
            self.assertTrue(str(e)=='Unlock function not implemented.')
        try:
            t.close()
        except NotImplementedError as e:
            self.assertTrue(str(e)=='Close function not implemented.')
        try:
            t.unclose()
        except NotImplementedError as e:
            self.assertTrue(str(e)=='Unclose function not implemented.')
        try:
            t.add_output()
        except NotImplementedError as e:
            self.assertTrue(str(e)=='Add_output function not implemented.')
        try:
            t.scrub()
        except  NotImplementedError as e:
            self.assertTrue(str(e)=='Scrub function not implemented.')
        try:
            t.set_error()
        except  NotImplementedError as e:
            self.assertTrue(str(e)=='set_error function not implemented.')

    def test_nested_modifier(self):
        t = NestedTokenModifier()
        self.assertTrue(t.timeout == 86400)
        t = NestedTokenModifier(10000)
        self.assertTrue(t.timeout == 1000)
        

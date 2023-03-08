# test_with_unittest.py

from unittest import TestCase
from file_sort import FileSort

class TryTesting(TestCase):
#     def test_always_passes(self):
#         self.assertTrue(True)

#     def test_always_fails(self):
#         self.assertTrue(False)

  def test_strip_file_name(self):
      filename = "i.am_a_test+file-for'py,test"
      fsort = FileSort(".", ".")
      cleaned = fsort.strip_file_name(filename)
      self.assertTrue(cleaned == "i am a test file for py test")

  def test_inspect_file(self):
     folder_strings = ["Test", "Name"]

     fsort = FileSort(".", ".")

     file_name1 = "Test Name.txt"    
     self.assertTrue(fsort.inspect_file(folder_strings, file_name1) == "Test Name.txt")
     
     file_name2 = "Test Name1.txt"
     self.assertFalse(fsort.inspect_file(folder_strings, file_name2))

  def test_get_matches(self):
     foldername = "Test Name"
     fileslist = [ "testname.txt", "test-name.txt", "Test_NAME.txt", "no-match.txt" ]
     fsort = FileSort(".", ".")
     result = fsort.get_matches(foldername, fileslist)
     self.assertTrue(result ==  ["testname.txt", "test-name.txt", "Test_NAME.txt"])
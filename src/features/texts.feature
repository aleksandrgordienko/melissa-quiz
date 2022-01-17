Feature: Texts class

  Scenario: all the tests on Texts class
     Given a Texts instance
      When loading language files
       And invoking get_text() for each key
      Then the values are the same as in JSON files
      When invoking check_bad()
       And with bad words
      Then True returned for each word
      When with good words
      Then False returned for each word
      When invoking get_joke()
      Then jokes returned from texts

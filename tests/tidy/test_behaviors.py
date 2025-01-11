import unittest
import simfile
from simfile.tidy import tidy
from simfile._private.dedent import dedent_and_trim
from simfile.tidy.behaviors import Whitespace


class TestWhitespace(unittest.TestCase):
    def test_sm5_sm(self):
        self.maxDiff = None
        sim_string = dedent_and_trim(
            """
            #TITLE:Song title;#SUBTITLE:Song subtitle;
                        
                #ARTIST:Song artist;
            #NOTES:
            dance-single:

            http\\:\\//stepartist.example: // contrived use of escapes
            Beginner:
            1:
            0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            0000
            0000
            0000
            0000;
            // comment
                        #NOTES:
                 dance-single:
                 :
                 Easy:
                 3:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            // measure 0
            1000
            0100
            0010
            0001
            , // measure 1
            0100
            0010
            1000
            0001
            ; // trailing comment SM"""
        )

        expected = dedent_and_trim(
            """
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;

            #NOTES:
                 dance-single:
                 http\\:\\//stepartist.example:
                 Beginner:
                 1:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            0000
            0000
            0000
            0000
            ;

            // comment
            #NOTES:
                 dance-single:
                 :
                 Easy:
                 3:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            // measure 0
            1000
            0100
            0010
            0001
            , // measure 1
            0100
            0010
            1000
            0001
            ; // trailing comment SM
            """
        )

        sim = simfile.loads(sim_string)
        self.assertTrue(tidy(sim, whitespace=Whitespace.SM5))
        self.assertEqual(expected, str(sim))
        # Validity check
        self.assertEqual(sim, simfile.loads(str(sim)))
        # Idempotency check
        self.assertFalse(tidy(sim, whitespace=Whitespace.SM5))

    def test_sm5_ssc(self):
        self.maxDiff = None
        sim_string = dedent_and_trim(
            """
            #VERSION:0.83;
            #TITLE:Song title;#SUBTITLE:Song subtitle;
                        
                #ARTIST:Song artist;
            #NOTEDATA:;
            #STEPSTYPE:dance-single;#DIFFICULTY:Beginner;
            #METER:1;

            #CREDIT:http\\:\\//stepartist.example; // contrived use of escapes

            #NOTES:
            0000
            0000
            0000
            0000
            ;
            // comment

            
            #NOTEDATA:;
            #STEPSTYPE:dance-single;#DIFFICULTY:Easy;
            
            #METER:3;
            #NOTES:
            // measure 0
            1000
            0100
            0010
            0001
            , // measure 1
            0100
            0010
            1000
            0001
            ; // trailing comment"""
        )
        expected = dedent_and_trim(
            """
            #VERSION:0.83;
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;

            #NOTEDATA:;
            #STEPSTYPE:dance-single;
            #DIFFICULTY:Beginner;
            #METER:1;
            #CREDIT:http\\:\\//stepartist.example; // contrived use of escapes
            #NOTES:
            0000
            0000
            0000
            0000
            ;

            // comment
            #NOTEDATA:;
            #STEPSTYPE:dance-single;
            #DIFFICULTY:Easy;
            #METER:3;
            #NOTES:
            // measure 0
            1000
            0100
            0010
            0001
            , // measure 1
            0100
            0010
            1000
            0001
            ; // trailing comment
            """
        )

        sim = simfile.loads(sim_string)
        self.assertTrue(tidy(sim, whitespace=Whitespace.SM5))
        self.assertEqual(expected, str(sim))
        # Validity check
        self.assertEqual(sim, simfile.loads(str(sim)))
        # Idempotency check
        self.assertFalse(tidy(sim, whitespace=Whitespace.SM5))

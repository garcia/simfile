import unittest
import simfile
from simfile.tidy import tidy
from simfile._private.dedent import dedent_and_trim
from simfile.tidy.behaviors import Whitespace


class TestWhitespace(unittest.TestCase):
    def test_sm5_sm(self):
        self.maxDiff = None
        text = dedent_and_trim(
            """
            #TITLE:Song title;#SUBTITLE:Song subtitle;
                        
                #ARTIST:Song artist;
            #NOTES:
            dance-single:
            :
            Beginner:
            1:
            0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            0000
            0000
            0000
            0000;
                        #NOTES:
            dance-single:
            :
            Easy:
            3:
            0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            1000
            0000
            0000
            0000;"""
        )

        sim = simfile.loads(text)

        tidy(sim, whitespace=Whitespace.SM5)

        expected = dedent_and_trim(
            """
            #TITLE:Song title;
            #SUBTITLE:Song subtitle;
            #ARTIST:Song artist;

            #NOTES:
                 dance-single:
                 :
                 Beginner:
                 1:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            0000
            0000
            0000
            0000
            ;

            #NOTES:
                 dance-single:
                 :
                 Easy:
                 3:
                 0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000:
            1000
            0000
            0000
            0000
            ;
            """
        )

        self.assertEqual(expected, str(sim))

    def test_sm5_ssc(self):
        self.maxDiff = None
        text = dedent_and_trim(
            """
            #VERSION:0.83;
            #TITLE:Song title;#SUBTITLE:Song subtitle;
                        
                #ARTIST:Song artist;
            #NOTEDATA:;
            #STEPSTYPE:dance-single;#DIFFICULTY:Beginner;
            
            #METER:1;
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
            1000
            0000
            0000
            0000
            ;"""
        )

        sim = simfile.loads(text)

        tidy(sim, whitespace=Whitespace.SM5)

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
            1000
            0000
            0000
            0000
            ;
            """
        )

        self.assertEqual(expected, str(sim))

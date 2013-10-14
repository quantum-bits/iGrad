#!/usr/bin/python

from keys import NAME, COURSES, SUB_REQ, EXCEPT

ORIENTATION = {NAME : 'Orientation Foundation', COURSES : ('IAS 101',)}
SPIRITUAL_FOUNDATION = {NAME : 'Spiritual Foundation' , 
                        COURSES : ('IAS 110',
                                   'BIB 110',
                                   'BIB 210',
                                   'REL 313',
                                   'PHI 413',
                                   'IAS 495',)}

STEWARDSHIP_OPTIONS = {NAME : 'Stewardship Options Foundation',
                       COURSES : ('PHP 200',
                                  'PHP 250',
                                  'PHP 280',
                                  'PHP 300',
                                  'PHP 302',
                                  'PHP 333',
                                  'PHP 334',
                                  'PHP 345',)}

STEWARDSHIP_OF_THE_BODY = {NAME : 'Stewardship of the Body', 
                           COURSES : ('PHP 100',),
                           SUB_REQ : (STEWARDSHIP_OPTIONS,)}

FINE_ARTS_OPTIONS = {NAME : 'Fine Arts Options Foundation', 
                     COURSES : ('HUM 250', 
                                'MCM 332',)}
FINE_ARTS = {NAME : 'Fine Arts Foundation', 
             COURSES : ('HUM 230', 'HUM 330',)}

SPEAKING = {NAME : 'Speaking Foundation', 
            COURSES : ('CAS 110', 'CAS 120',)}

WRITING = {NAME : 'Writing Foundation',
           COURSES : ('ENG 110',)}

HISTORY = {NAME : 'History Foundation',
           COURSES : ('HIS*',),
           EXCEPT  : ('HIS 130', 
                      'HIS 250',
                      'HIS 360',
                      'HIS 393',
                      'HIS 480',
                      'HIS 490',)}

COMPUTER_SCIENCE = {NAME : 'Computer Science Foundation', 
                    COURSES : ('COS 104', 'COS 105', 'COS 106',)}

MATHEMATICS = {NAME : 'Mathematics Foundation', 
               COURSES : ('MAT 100', 
                          'MAT 120',
                          'MAT 140',
                          'MAT 145',
                          'MAT 151',
                          'MAT 180',
                          'MAT 210',
                          'MAT 220',
                          'MAT 301-302',
                          'SOC 355',)}

LITERATURE = {NAME : 'Literature Foundation',
              COURSES : ('CAT 200', 
                         'ENG 230',
                         'ENG 240',
                         'ENG 250',
                         'SPA 331',
                         'SPA 332',
                         'SPA 421',
                         'SPA 422',)}

PHYSICAL_SCIENCE = {NAME : 'Physical Science Foundation',
                    COURSES : ('CHE 100', 
                               'CHE 120',
                               'CHE 201',
                               'CHE 211', 
                               'PHY 120',
                               'PHY 203',
                               'PHY 211',)}

LIFE_SCIENCE = {NAME : 'Life Science Foundation', 
                COURSES : ('BIO 100',
                           'BIO 101',
                           'BIO 103',
                           'BIO 104',
                           'BIO 200',
                           'BIO 205',
                           'BIO 243',
                           'BIO 244',
                           'CHE 120',
                           'ENS 200',
                           'ENS 231',)}

EARTH_SCIENCE = {NAME : 'Earth Science Foundation', 
                 COURSES : ('ENP 345', 
                           'ENS 241', 
                           'ENS 242',
                           'GEO 210',
                           'GEO 240',
                           'PHY 201',)}

SCIENCE = {NAME : 'Science Foundation', 
           SUB_REQ : (LIFE_SCIENCE, PHYSICAL_SCIENCE, EARTH_SCIENCE,)}
                    

CIVIC_ENGAGEMENT = {NAME : 'Civic Engagment Foundation', 
                    COURSES : ('ECO 190',
                               'ECO 201',
                               'ECO 202',
                               'GEO 230',
                               'PBH 100',
                               'PHP 346',
                               'POS 100',
                               'POS 150',
                               'POS 213',
                               'POS 331',
                               'SOC 100',
                               'SOC 110',
                               'SOC 210',
                               'SOC 220',
                               'SOC 410',
                               'SWK 200',
                               'SWK 320',)}

GENERAL_SOCIAL_SCIENCE = {NAME : 'General Social Science Foundation',
                          COURSES : ('GEO 220',
                                     'HIS 211/311', 
                                     'HIS 212/312',
                                     'IAS 330',
                                     'POS 222',
                                     'POS 312',
                                     'POS 321',
                                     'PSY 110',
                                     'PSY 200',
                                     'PSY 240',
                                     'PSY 250',
                                     'PSY 340', 
                                     'PSY 350',
                                     'SOC 200',
                                     'SOC 310',
                                     'SOC 330',
                                     'SOC 361',
                                     'SOC 381',)}

SOCIAL_SCIENCE = {NAME : 'Social Science Foundation',
                  SUB_REQ : (CIVIC_ENGAGEMENT, GENERAL_SOCIAL_SCIENCE,)}

FOUNDATION_CORE = {NAME : 'Foundational Core',
                   SUB_REQ : (ORIENTATION,
                              SPIRITUAL_FOUNDATION, 
                              STEWARDSHIP_OF_THE_BODY,
                              FINE_ARTS, 
                              SPEAKING,
                              WRITING,
                              HISTORY,
                              COMPUTER_SCIENCE,
                              MATHEMATICS,
                              LITERATURE,
                              SCIENCE,
                              SOCIAL_SCIENCE,)}



requirements = [ORIENTATION,
                SPIRITUAL_FOUNDATION, 
                STEWARDSHIP_OPTIONS,
                STEWARDSHIP_OF_THE_BODY,
                FINE_ARTS_OPTIONS,
                FINE_ARTS, 
                SPEAKING,
                WRITING,
                HISTORY,
                COMPUTER_SCIENCE,
                MATHEMATICS,
                LITERATURE,
                PHYSICAL_SCIENCE,
                LIFE_SCIENCE,
                EARTH_SCIENCE,
                SCIENCE,
                CIVIC_ENGAGEMENT,
                GENERAL_SOCIAL_SCIENCE,
                SOCIAL_SCIENCE,
                FOUNDATION_CORE]


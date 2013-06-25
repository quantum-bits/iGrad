# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CreditHour'
        db.create_table(u'planner_credithour', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'planner', ['CreditHour'])

        # Adding field 'Course.credit_hour'
        db.add_column(u'planner_course', 'credit_hour',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses', null=True, to=orm['planner.CreditHour']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'CreditHour'
        db.delete_table(u'planner_credithour')

        # Deleting field 'Course.credit_hour'
        db.delete_column(u'planner_course', 'credit_hour_id')


    models = {
        u'planner.academicyear': {
            'Meta': {'ordering': "['begin_on']", 'object_name': 'AcademicYear'},
            'begin_on': ('django.db.models.fields.DateField', [], {}),
            'end_on': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'planner.advisingnote': {
            'Meta': {'object_name': 'AdvisingNote'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'advising_notes'", 'to': u"orm['planner.Student']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.building': {
            'Meta': {'object_name': 'Building'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.classmeeting': {
            'Meta': {'object_name': 'ClassMeeting'},
            'begin_at': ('django.db.models.fields.TimeField', [], {}),
            'course_offering': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'class_meetings'", 'to': u"orm['planner.CourseOffering']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_at': ('django.db.models.fields.TimeField', [], {}),
            'held_on': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.FacultyMember']"}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.Room']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.classstanding': {
            'Meta': {'ordering': "['seq']", 'object_name': 'ClassStanding'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'seq': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'})
        },
        u'planner.constraint': {
            'Meta': {'object_name': 'Constraint'},
            'constraint_text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'planner.course': {
            'Meta': {'ordering': "['subject', 'number', 'title']", 'unique_together': "(('subject', 'number'),)", 'object_name': 'Course'},
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'courses'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['planner.CourseAttribute']"}),
            'coreqs': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'coreq_for'", 'blank': 'True', 'to': u"orm['planner.Requirement']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit_hour': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'null': 'True', 'to': u"orm['planner.CreditHour']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_credit_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3'}),
            'min_credit_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'prereqs': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'prereq_for'", 'blank': 'True', 'to': u"orm['planner.Requirement']"}),
            'schedule_semester': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['planner.SemesterName']", 'symmetrical': 'False'}),
            'schedule_year': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': u"orm['planner.Subject']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.courseattribute': {
            'Meta': {'object_name': 'CourseAttribute'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.courseoffering': {
            'Meta': {'object_name': 'CourseOffering'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offerings'", 'to': u"orm['planner.Course']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'course_offerings'", 'to': u"orm['planner.FacultyMember']", 'through': u"orm['planner.OfferingInstructor']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.Semester']"}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.coursesubstitution': {
            'Meta': {'object_name': 'CourseSubstitution'},
            'credit_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3'}),
            'equivalent_course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'course_substitutions'", 'to': u"orm['planner.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.Semester']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'course_substitutions'", 'to': u"orm['planner.Student']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'course_substitutions'", 'null': 'True', 'to': u"orm['planner.University']"})
        },
        u'planner.coursetaken': {
            'Meta': {'object_name': 'CourseTaken'},
            'course_offering': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.CourseOffering']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'final_grade': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.Grade']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses_taken'", 'to': u"orm['planner.Student']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.credithour': {
            'Meta': {'object_name': 'CreditHour'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'planner.degreeprogram': {
            'Meta': {'object_name': 'DegreeProgram'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entering_year': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'major': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'degree_programs'", 'to': u"orm['planner.Major']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.degreeprogramcourse': {
            'Meta': {'object_name': 'DegreeProgramCourse'},
            'class_standing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.ClassStanding']"}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.Course']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'degree_program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.DegreeProgram']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.SemesterName']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.department': {
            'Meta': {'object_name': 'Department'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'chair': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'department_chaired'", 'unique': 'True', 'null': 'True', 'to': u"orm['planner.FacultyMember']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'departments'", 'to': u"orm['planner.School']"})
        },
        u'planner.facultymember': {
            'Meta': {'object_name': 'FacultyMember', '_ormbases': [u'planner.Person']},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'faculty'", 'to': u"orm['planner.Department']"}),
            'faculty_id': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['planner.Person']", 'unique': 'True', 'primary_key': 'True'}),
            'rank': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'faculty'", 'to': u"orm['planner.University']"})
        },
        u'planner.grade': {
            'Meta': {'object_name': 'Grade'},
            'grade_points': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'letter_grade': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        u'planner.holiday': {
            'Meta': {'ordering': "['begin_on']", 'object_name': 'Holiday'},
            'begin_on': ('django.db.models.fields.DateField', [], {}),
            'end_on': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holidays'", 'to': u"orm['planner.Semester']"})
        },
        u'planner.major': {
            'Meta': {'object_name': 'Major'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'majors'", 'to': u"orm['planner.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'planner.minor': {
            'Meta': {'object_name': 'Minor'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'minors'", 'to': u"orm['planner.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'planner.offeringinstructor': {
            'Meta': {'object_name': 'OfferingInstructor'},
            'course_offering': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.CourseOffering']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.FacultyMember']"}),
            'load_credit': ('django.db.models.fields.FloatField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.person': {
            'Meta': {'object_name': 'Person'},
            'cell_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'work_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'planner.plannedcourse': {
            'Meta': {'object_name': 'PlannedCourse'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offering': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['planner.CourseOffering']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'planned_courses'", 'to': u"orm['planner.Student']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.requirement': {
            'Meta': {'ordering': "['display_name']", 'object_name': 'Requirement'},
            'constraints': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'constraints'", 'blank': 'True', 'to': u"orm['planner.Constraint']"}),
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'courses'", 'blank': 'True', 'to': u"orm['planner.Course']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'requirements': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sub_requirements'", 'blank': 'True', 'to': u"orm['planner.Requirement']"})
        },
        u'planner.room': {
            'Meta': {'object_name': 'Room'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rooms'", 'to': u"orm['planner.Building']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.school': {
            'Meta': {'object_name': 'School'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dean': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['planner.FacultyMember']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'schools'", 'to': u"orm['planner.University']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.semester': {
            'Meta': {'ordering': "['year', 'name']", 'object_name': 'Semester'},
            'begin_on': ('django.db.models.fields.DateField', [], {}),
            'end_on': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.SemesterName']"}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'semesters'", 'to': u"orm['planner.AcademicYear']"})
        },
        u'planner.semestername': {
            'Meta': {'ordering': "['seq']", 'object_name': 'SemesterName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'seq': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'})
        },
        u'planner.staffmember': {
            'Meta': {'object_name': 'StaffMember', '_ormbases': [u'planner.Person']},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'staff'", 'to': u"orm['planner.Department']"}),
            u'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['planner.Person']", 'unique': 'True', 'primary_key': 'True'}),
            'staff_id': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'staff'", 'to': u"orm['planner.University']"})
        },
        u'planner.student': {
            'Meta': {'object_name': 'Student', '_ormbases': [u'planner.Person']},
            'catalog_year': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['planner.AcademicYear']"}),
            'entering_year': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['planner.AcademicYear']"}),
            'majors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'students'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['planner.Major']"}),
            'minors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'students'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['planner.Minor']"}),
            u'person_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['planner.Person']", 'unique': 'True', 'primary_key': 'True'}),
            'student_id': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'students'", 'to': u"orm['planner.University']"})
        },
        u'planner.subject': {
            'Meta': {'ordering': "['abbrev']", 'object_name': 'Subject'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subjects'", 'null': 'True', 'to': u"orm['planner.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'planner.university': {
            'Meta': {'object_name': 'University'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['planner']
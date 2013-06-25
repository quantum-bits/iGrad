# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table(u'planner_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('home_phone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('cell_phone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('work_phone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'planner', ['Person'])

        # Adding model 'University'
        db.create_table(u'planner_university', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'planner', ['University'])

        # Adding model 'School'
        db.create_table(u'planner_school', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(related_name='schools', to=orm['planner.University'])),
            ('dean', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['planner.FacultyMember'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'planner', ['School'])

        # Adding model 'Department'
        db.create_table(u'planner_department', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(related_name='departments', to=orm['planner.School'])),
            ('chair', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='department_chaired', unique=True, null=True, to=orm['planner.FacultyMember'])),
        ))
        db.send_create_signal(u'planner', ['Department'])

        # Adding model 'Major'
        db.create_table(u'planner_major', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='majors', to=orm['planner.Department'])),
        ))
        db.send_create_signal(u'planner', ['Major'])

        # Adding model 'Minor'
        db.create_table(u'planner_minor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='minors', to=orm['planner.Department'])),
        ))
        db.send_create_signal(u'planner', ['Minor'])

        # Adding model 'FacultyMember'
        db.create_table(u'planner_facultymember', (
            (u'person_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['planner.Person'], unique=True, primary_key=True)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(related_name='faculty', to=orm['planner.University'])),
            ('faculty_id', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='faculty', to=orm['planner.Department'])),
            ('rank', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal(u'planner', ['FacultyMember'])

        # Adding model 'StaffMember'
        db.create_table(u'planner_staffmember', (
            (u'person_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['planner.Person'], unique=True, primary_key=True)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(related_name='staff', to=orm['planner.University'])),
            ('staff_id', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='staff', to=orm['planner.Department'])),
        ))
        db.send_create_signal(u'planner', ['StaffMember'])

        # Adding model 'AcademicYear'
        db.create_table(u'planner_academicyear', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('begin_on', self.gf('django.db.models.fields.DateField')()),
            ('end_on', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'planner', ['AcademicYear'])

        # Adding model 'SemesterName'
        db.create_table(u'planner_semestername', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('seq', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'planner', ['SemesterName'])

        # Adding model 'Semester'
        db.create_table(u'planner_semester', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.SemesterName'])),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(related_name='semesters', to=orm['planner.AcademicYear'])),
            ('begin_on', self.gf('django.db.models.fields.DateField')()),
            ('end_on', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'planner', ['Semester'])

        # Adding model 'Holiday'
        db.create_table(u'planner_holiday', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('begin_on', self.gf('django.db.models.fields.DateField')()),
            ('end_on', self.gf('django.db.models.fields.DateField')()),
            ('semester', self.gf('django.db.models.fields.related.ForeignKey')(related_name='holidays', to=orm['planner.Semester'])),
        ))
        db.send_create_signal(u'planner', ['Holiday'])

        # Adding model 'Building'
        db.create_table(u'planner_building', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'planner', ['Building'])

        # Adding model 'Room'
        db.create_table(u'planner_room', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rooms', to=orm['planner.Building'])),
        ))
        db.send_create_signal(u'planner', ['Room'])

        # Adding model 'Subject'
        db.create_table(u'planner_subject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subjects', null=True, to=orm['planner.Department'])),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal(u'planner', ['Subject'])

        # Adding model 'CourseAttribute'
        db.create_table(u'planner_courseattribute', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal(u'planner', ['CourseAttribute'])

        # Adding model 'Constraint'
        db.create_table(u'planner_constraint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('constraint_text', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'planner', ['Constraint'])

        # Adding model 'Requirement'
        db.create_table(u'planner_requirement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'planner', ['Requirement'])

        # Adding M2M table for field constraints on 'Requirement'
        m2m_table_name = db.shorten_name(u'planner_requirement_constraints')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('requirement', models.ForeignKey(orm[u'planner.requirement'], null=False)),
            ('constraint', models.ForeignKey(orm[u'planner.constraint'], null=False))
        ))
        db.create_unique(m2m_table_name, ['requirement_id', 'constraint_id'])

        # Adding M2M table for field requirements on 'Requirement'
        m2m_table_name = db.shorten_name(u'planner_requirement_requirements')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_requirement', models.ForeignKey(orm[u'planner.requirement'], null=False)),
            ('to_requirement', models.ForeignKey(orm[u'planner.requirement'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_requirement_id', 'to_requirement_id'])

        # Adding M2M table for field courses on 'Requirement'
        m2m_table_name = db.shorten_name(u'planner_requirement_courses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('requirement', models.ForeignKey(orm[u'planner.requirement'], null=False)),
            ('course', models.ForeignKey(orm[u'planner.course'], null=False))
        ))
        db.create_unique(m2m_table_name, ['requirement_id', 'course_id'])

        # Adding model 'Course'
        db.create_table(u'planner_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses', to=orm['planner.Subject'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('credit_hours', self.gf('django.db.models.fields.PositiveIntegerField')(default=3)),
            ('schedule_year', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'planner', ['Course'])

        # Adding unique constraint on 'Course', fields ['subject', 'number']
        db.create_unique(u'planner_course', ['subject_id', 'number'])

        # Adding M2M table for field prereqs on 'Course'
        m2m_table_name = db.shorten_name(u'planner_course_prereqs')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'planner.course'], null=False)),
            ('requirement', models.ForeignKey(orm[u'planner.requirement'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'requirement_id'])

        # Adding M2M table for field coreqs on 'Course'
        m2m_table_name = db.shorten_name(u'planner_course_coreqs')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'planner.course'], null=False)),
            ('requirement', models.ForeignKey(orm[u'planner.requirement'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'requirement_id'])

        # Adding M2M table for field attributes on 'Course'
        m2m_table_name = db.shorten_name(u'planner_course_attributes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'planner.course'], null=False)),
            ('courseattribute', models.ForeignKey(orm[u'planner.courseattribute'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'courseattribute_id'])

        # Adding M2M table for field schedule_semester on 'Course'
        m2m_table_name = db.shorten_name(u'planner_course_schedule_semester')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'planner.course'], null=False)),
            ('semestername', models.ForeignKey(orm[u'planner.semestername'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'semestername_id'])

        # Adding model 'Student'
        db.create_table(u'planner_student', (
            (u'person_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['planner.Person'], unique=True, primary_key=True)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(related_name='students', to=orm['planner.University'])),
            ('student_id', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('entering_year', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['planner.AcademicYear'])),
            ('catalog_year', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['planner.AcademicYear'])),
        ))
        db.send_create_signal(u'planner', ['Student'])

        # Adding M2M table for field majors on 'Student'
        m2m_table_name = db.shorten_name(u'planner_student_majors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('student', models.ForeignKey(orm[u'planner.student'], null=False)),
            ('major', models.ForeignKey(orm[u'planner.major'], null=False))
        ))
        db.create_unique(m2m_table_name, ['student_id', 'major_id'])

        # Adding M2M table for field minors on 'Student'
        m2m_table_name = db.shorten_name(u'planner_student_minors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('student', models.ForeignKey(orm[u'planner.student'], null=False)),
            ('minor', models.ForeignKey(orm[u'planner.minor'], null=False))
        ))
        db.create_unique(m2m_table_name, ['student_id', 'minor_id'])

        # Adding model 'CourseOffering'
        db.create_table(u'planner_courseoffering', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offerings', to=orm['planner.Course'])),
            ('semester', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.Semester'])),
        ))
        db.send_create_signal(u'planner', ['CourseOffering'])

        # Adding model 'Grade'
        db.create_table(u'planner_grade', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('letter_grade', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('grade_points', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'planner', ['Grade'])

        # Adding model 'CourseTaken'
        db.create_table(u'planner_coursetaken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses_taken', to=orm['planner.Student'])),
            ('course_offering', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.CourseOffering'])),
            ('final_grade', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.Grade'], blank=True)),
        ))
        db.send_create_signal(u'planner', ['CourseTaken'])

        # Adding model 'OfferingInstructor'
        db.create_table(u'planner_offeringinstructor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('course_offering', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.CourseOffering'])),
            ('instructor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.FacultyMember'])),
            ('load_credit', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'planner', ['OfferingInstructor'])

        # Adding model 'ClassMeeting'
        db.create_table(u'planner_classmeeting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('held_on', self.gf('django.db.models.fields.DateField')()),
            ('begin_at', self.gf('django.db.models.fields.TimeField')()),
            ('end_at', self.gf('django.db.models.fields.TimeField')()),
            ('course_offering', self.gf('django.db.models.fields.related.ForeignKey')(related_name='class_meetings', to=orm['planner.CourseOffering'])),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.Room'])),
            ('instructor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.FacultyMember'])),
        ))
        db.send_create_signal(u'planner', ['ClassMeeting'])

        # Adding model 'RequirementBlock'
        db.create_table(u'planner_requirementblock', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('requirement_type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('minimum_number_of_credit_hours', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('list_order', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('text_for_user', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'planner', ['RequirementBlock'])

        # Adding M2M table for field courses on 'RequirementBlock'
        m2m_table_name = db.shorten_name(u'planner_requirementblock_courses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('requirementblock', models.ForeignKey(orm[u'planner.requirementblock'], null=False)),
            ('course', models.ForeignKey(orm[u'planner.course'], null=False))
        ))
        db.create_unique(m2m_table_name, ['requirementblock_id', 'course_id'])

        # Adding model 'TransferCourse'
        db.create_table(u'planner_transfercourse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('university', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfer_courses', to=orm['planner.University'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('credit_hours', self.gf('django.db.models.fields.PositiveIntegerField')(default=3)),
            ('semester', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.Semester'])),
            ('equivalent_course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfer_courses', to=orm['planner.Course'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transfer_courses', to=orm['planner.Student'])),
        ))
        db.send_create_signal(u'planner', ['TransferCourse'])

        # Adding model 'AdvisingNote'
        db.create_table(u'planner_advisingnote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(related_name='advising_notes', to=orm['planner.Student'])),
            ('note', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'planner', ['AdvisingNote'])

        # Adding model 'ClassStanding'
        db.create_table(u'planner_classstanding', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('seq', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'planner', ['ClassStanding'])

        # Adding model 'DegreeProgram'
        db.create_table(u'planner_degreeprogram', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('entering_year', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('major', self.gf('django.db.models.fields.related.ForeignKey')(related_name='degree_programs', to=orm['planner.Major'])),
        ))
        db.send_create_signal(u'planner', ['DegreeProgram'])

        # Adding model 'DegreeProgramCourse'
        db.create_table(u'planner_degreeprogramcourse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('degree_program', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.DegreeProgram'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.Course'])),
            ('class_standing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.ClassStanding'])),
            ('semester_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planner.SemesterName'])),
        ))
        db.send_create_signal(u'planner', ['DegreeProgramCourse'])


    def backwards(self, orm):
        # Removing unique constraint on 'Course', fields ['subject', 'number']
        db.delete_unique(u'planner_course', ['subject_id', 'number'])

        # Deleting model 'Person'
        db.delete_table(u'planner_person')

        # Deleting model 'University'
        db.delete_table(u'planner_university')

        # Deleting model 'School'
        db.delete_table(u'planner_school')

        # Deleting model 'Department'
        db.delete_table(u'planner_department')

        # Deleting model 'Major'
        db.delete_table(u'planner_major')

        # Deleting model 'Minor'
        db.delete_table(u'planner_minor')

        # Deleting model 'FacultyMember'
        db.delete_table(u'planner_facultymember')

        # Deleting model 'StaffMember'
        db.delete_table(u'planner_staffmember')

        # Deleting model 'AcademicYear'
        db.delete_table(u'planner_academicyear')

        # Deleting model 'SemesterName'
        db.delete_table(u'planner_semestername')

        # Deleting model 'Semester'
        db.delete_table(u'planner_semester')

        # Deleting model 'Holiday'
        db.delete_table(u'planner_holiday')

        # Deleting model 'Building'
        db.delete_table(u'planner_building')

        # Deleting model 'Room'
        db.delete_table(u'planner_room')

        # Deleting model 'Subject'
        db.delete_table(u'planner_subject')

        # Deleting model 'CourseAttribute'
        db.delete_table(u'planner_courseattribute')

        # Deleting model 'Constraint'
        db.delete_table(u'planner_constraint')

        # Deleting model 'Requirement'
        db.delete_table(u'planner_requirement')

        # Removing M2M table for field constraints on 'Requirement'
        db.delete_table(db.shorten_name(u'planner_requirement_constraints'))

        # Removing M2M table for field requirements on 'Requirement'
        db.delete_table(db.shorten_name(u'planner_requirement_requirements'))

        # Removing M2M table for field courses on 'Requirement'
        db.delete_table(db.shorten_name(u'planner_requirement_courses'))

        # Deleting model 'Course'
        db.delete_table(u'planner_course')

        # Removing M2M table for field prereqs on 'Course'
        db.delete_table(db.shorten_name(u'planner_course_prereqs'))

        # Removing M2M table for field coreqs on 'Course'
        db.delete_table(db.shorten_name(u'planner_course_coreqs'))

        # Removing M2M table for field attributes on 'Course'
        db.delete_table(db.shorten_name(u'planner_course_attributes'))

        # Removing M2M table for field schedule_semester on 'Course'
        db.delete_table(db.shorten_name(u'planner_course_schedule_semester'))

        # Deleting model 'Student'
        db.delete_table(u'planner_student')

        # Removing M2M table for field majors on 'Student'
        db.delete_table(db.shorten_name(u'planner_student_majors'))

        # Removing M2M table for field minors on 'Student'
        db.delete_table(db.shorten_name(u'planner_student_minors'))

        # Deleting model 'CourseOffering'
        db.delete_table(u'planner_courseoffering')

        # Deleting model 'Grade'
        db.delete_table(u'planner_grade')

        # Deleting model 'CourseTaken'
        db.delete_table(u'planner_coursetaken')

        # Deleting model 'OfferingInstructor'
        db.delete_table(u'planner_offeringinstructor')

        # Deleting model 'ClassMeeting'
        db.delete_table(u'planner_classmeeting')

        # Deleting model 'RequirementBlock'
        db.delete_table(u'planner_requirementblock')

        # Removing M2M table for field courses on 'RequirementBlock'
        db.delete_table(db.shorten_name(u'planner_requirementblock_courses'))

        # Deleting model 'TransferCourse'
        db.delete_table(u'planner_transfercourse')

        # Deleting model 'AdvisingNote'
        db.delete_table(u'planner_advisingnote')

        # Deleting model 'ClassStanding'
        db.delete_table(u'planner_classstanding')

        # Deleting model 'DegreeProgram'
        db.delete_table(u'planner_degreeprogram')

        # Deleting model 'DegreeProgramCourse'
        db.delete_table(u'planner_degreeprogramcourse')


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
            'credit_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        u'planner.requirement': {
            'Meta': {'ordering': "['display_name']", 'object_name': 'Requirement'},
            'constraints': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'constraints'", 'blank': 'True', 'to': u"orm['planner.Constraint']"}),
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'courses'", 'blank': 'True', 'to': u"orm['planner.Course']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'requirements': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sub_requirements'", 'blank': 'True', 'to': u"orm['planner.Requirement']"})
        },
        u'planner.requirementblock': {
            'Meta': {'ordering': "['name']", 'object_name': 'RequirementBlock'},
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['planner.Course']", 'symmetrical': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list_order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'minimum_number_of_credit_hours': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'requirement_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'text_for_user': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
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
        u'planner.transfercourse': {
            'Meta': {'object_name': 'TransferCourse'},
            'credit_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3'}),
            'equivalent_course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transfer_courses'", 'to': u"orm['planner.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planner.Semester']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transfer_courses'", 'to': u"orm['planner.Student']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transfer_courses'", 'to': u"orm['planner.University']"})
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
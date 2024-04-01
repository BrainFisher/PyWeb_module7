from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, desc
import random
from faker import Faker

# Створення бази даних
engine = create_engine('sqlite:///students.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Оголошення моделей


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    students = relationship("Student", back_populates="group")


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))

    group = relationship("Group", back_populates="students")
    grades = relationship("Grade", back_populates="student")


class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    subjects = relationship("Subject", back_populates="teacher")


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    subject_name = Column(String)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))

    teacher = relationship("Teacher", back_populates="subjects")
    grades = relationship("Grade", back_populates="subject")


class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))

    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")


# Створення таблиць у базі даних
Base.metadata.create_all(engine)


# Наповнення бази даних випадковими даними
def seed_db(session):
    fake = Faker()

    groups = [Group(name=f"Group {i}") for i in range(1, 4)]
    session.add_all(groups)
    session.commit()

    teachers = [Teacher(fullname=fake.name()) for _ in range(5)]
    session.add_all(teachers)
    session.commit()

    subjects = [Subject(subject_name=f"Subject {
                        i}", teacher=random.choice(teachers)) for i in range(1, 9)]
    session.add_all(subjects)
    session.commit()

    students = [Student(fullname=fake.name(), group=random.choice(groups))
                for _ in range(30)]
    session.add_all(students)
    session.commit()

    grades = [Grade(value=random.randint(1, 10), student=random.choice(students), subject=random.choice(subjects))
              for _ in range(20)]
    session.add_all(grades)
    session.commit()


# Вибірка 1: Знайти 5 студентів із найбільшим середнім балом з усіх предметів
def select_1(session):
    return session.query(Student.fullname, func.round(func.avg(Grade.value), 2).label('avg_grade')) \
        .join(Grade).group_by(Student.id).order_by(desc('avg_grade')).limit(5).all()


# Вибірка 2: Знайти студента із найвищим середнім балом з певного предмета
def select_2(session, subject_name):
    return session.query(Student.fullname, func.round(func.avg(Grade.value), 2).label('avg_grade')) \
        .join(Grade).join(Subject).filter(Subject.subject_name == subject_name) \
        .group_by(Student.id).order_by(desc('avg_grade')).first()


# Вибірка 3: Знайти середній бал у групах з певного предмета
def select_3(session, subject_name):
    return session.query(Group.name, func.round(func.avg(Grade.value), 2).label('avg_grade')) \
        .join(Student, Group.students) \
        .join(Grade, Student.grades) \
        .join(Subject, Grade.subject) \
        .filter(Subject.subject_name == subject_name) \
        .group_by(Group.id).all()


# Вибірка 4: Знайти середній бал на потоці (по всій таблиці оцінок)
def select_4(session):
    return session.query(func.round(func.avg(Grade.value), 2).label('avg_grade')).all()


# Вибірка 5: Знайти які курси читає певний викладач
def select_5(session, teacher_name):
    return session.query(Subject.subject_name).join(Subject.teacher).filter(Teacher.fullname == teacher_name).all()


# Вибірка 6: Знайти список студентів у певній групі
def select_6(session, group_name):
    return session.query(Student.fullname).join(Student.group).filter(Group.name == group_name).all()


# Вибірка 7: Знайти оцінки студентів у окремій групі з певного предмета
def select_7(session, group_name, subject_name):
    return session.query(Student.fullname, Grade.value).join(Student.group).join(Grade).join(Grade.subject) \
        .filter(Group.name == group_name, Subject.subject_name == subject_name).all()


# Вибірка 8: Знайти середній бал, який ставить певний викладач зі своїх предметів
def select_8(session, teacher_name):
    return session.query(func.round(func.avg(Grade.value), 2).label('avg_grade')) \
        .join(Subject).join(Subject.teacher).filter(Teacher.fullname == teacher_name).all()


# Вибірка 9: Знайти список курсів, які відвідує певний студент
def select_9(session, student_name):
    return session.query(Subject.subject_name).join(Grade).join(Student).filter(Student.fullname == student_name).all()


# Вибірка 10: Список курсів, які певному студенту читає певний викладач
def select_10(session, student_name, teacher_name):
    return session.query(Subject.subject_name) \
        .join(Grade).join(Student).join(Subject.teacher).filter(Student.fullname == student_name,
                                                                Teacher.fullname == teacher_name).all()


# Створення бази даних та заповнення даними
seed_db(session)

# Виведення результатів вибірок
print("Select 1:", select_1(session))
print("Select 2:", select_2(session, "Mathematics"))
print("Select 3:", select_3(session, "Mathematics"))
print("Select 4:", select_4(session))
print("Select 5:", select_5(session, "Mr. Smith"))
print("Select 6:", select_6(session, "Group A"))
print("Select 7:", select_7(session, "Group A", "Mathematics"))
print("Select 8:", select_8(session, "Mr. Smith"))
print("Select 9:", select_9(session, "John Doe"))
print("Select 10:", select_10(session, "John Doe", "Mr. Smith"))

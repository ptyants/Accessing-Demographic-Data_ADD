from server import app, db, CitizenInfo, PersonInfo, LifeStatus, Household

# Drop all existing tables
db.drop_all()

# Create the tables
db.create_all()

# Create sample data
with app.app_context():
    # LifeStatus
    ls1 = LifeStatus(ns="Single", describe="Not married")
    ls2 = LifeStatus(ns="Married", describe="Currently married")
    db.session.add_all([ls1, ls2])
    db.session.commit()

    # CitizenInfo
    citizen1 = CitizenInfo(name="John Doe", household_id=None, person_info_id=None)
    citizen2 = CitizenInfo(name="Jane Doe", household_id=None, person_info_id=None)
    db.session.add_all([citizen1, citizen2])
    db.session.commit()

    # PersonInfo
    person1 = PersonInfo(
        address="123 Main St",
        father_id=None,
        mother_id=None,
        ls_id=1,
        ms="Single",
        born_in="City A",
        date_birth="1990-01-01"
    )
    person2 = PersonInfo(
        address="456 Broad St",
        father_id=None,
        mother_id=None,
        ls_id=2,
        ms="Married",
        born_in="City B",
        date_birth="1992-05-15"
    )
    db.session.add_all([person1, person2])
    db.session.commit()

    # Household
    household1 = Household(address="789 Elm St", hh=None)
    household2 = Household(address="101 Pine St", hh=None)
    db.session.add_all([household1, household2])
    db.session.commit()

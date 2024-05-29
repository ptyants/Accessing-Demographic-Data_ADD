from server import db

class Citizen_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable = False)
    houseHold_id = db.Column(db.Integer, db.ForeignKey('household.id'))
    person_info_id = db.Column(db.Integer, db.ForeignKey('person_info.id'))

    def __init__(self, name, houseHold_id, person_info_id):
        self.name = name
        self.houseHold_id = houseHold_id
        self.person_info_id = person_info_id


class Person_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100))
    father_id = db.Column(db.Integer, db.ForeignKey('citizen_info.id'))
    mother_id = db.Column(db.Integer, db.ForeignKey('citizen_info.id'))
    Ls_id = db.Column(db.Integer, db.ForeignKey('life_status.id'))
    Ms = db.Column(db.String(100))
    born_in = db.Column(db.String(100), nullable = False)
    date_birth = db.Column(db.Date)

    def __init__(self, address, father_id, mother_id, Ls_id, Ms, born_in, date_birth):
        self.address = address
        self.father_id = father_id
        self.mother_id = mother_id
        self.Ls_id = Ls_id
        self.Ms = Ms
        self.born_in = born_in
        self.date_birth = date_birth



class Life_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Ns = db.Column(db.String(100), nullable = False)
    describe = db.Column(db.String(100))

    def __init__(self, Ns, describe):
        self.Ns = Ns
        self.describe = describe



class Household(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable = False)
    HH = db.Column(db.Integer, db.ForeignKey('citizen_info.id'))

    def __init__(self, address, HH):
        self.address = address
        self.HH = HH


    
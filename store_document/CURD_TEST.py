from flask import current_app
from sqlalchemy.orm.exc import NoResultFound

class CRUD_Life_status():
    @staticmethod
    def create_life_status(Ns, describe):
        life_status = Life_status(Ns=Ns, describe=describe)
        db.session.add(life_status)
        db.session.commit()
        return life_status
    
    @staticmethod
    def get_all_life_status():
        return Life_status.query.all()

    @staticmethod
    def get_life_status_by_id(life_status_id):
        try:
            life_status = Life_status.query.filter_by(id=life_status_id).one()
            return life_status
        except NoResultFound:
            return None

    @staticmethod
    def update_life_status(life_status_id, Ns=None, describe=None):
        life_status = CRUD_Life_status.get_life_status_by_id(life_status_id)
        if life_status:
            if Ns is not None:
                life_status.Ns = Ns
            if describe is not None:
                life_status.describe = describe
            db.session.commit()
            return life_status
        return None

    @staticmethod
    def delete_life_status(life_status_id):
        life_status = CRUD_Life_status.get_life_status_by_id(life_status_id)
        if life_status:
            db.session.delete(life_status)
            db.session.commit()
            return True
        return False
    

# Create
new_life_status = CRUD_Life_status.create_life_status(Ns='Married', describe='Happily married')
print(new_life_status.id)  # Access the ID of the newly created life_status

# Read
retrieved_life_status = CRUD_Life_status.get_life_status_by_id(new_life_status.id)
print(retrieved_life_status.Ns, retrieved_life_status.describe)

# Update
CRUD_Life_status.update_life_status(new_life_status.id, Ns='Single')
updated_life_status = CRUD_Life_status.get_life_status_by_id(new_life_status.id)
print(updated_life_status.Ns)

# Delete
result = CRUD_Life_status.delete_life_status(new_life_status.id)
print(result)  # True if deletion is successful, False otherwise



from flask import jsonify

def get_life_status():
    life_status_data = CRUD_Life_status.get_all_life_status()

    life_status_list = []
    for life_status in life_status_data:
        life_status_list.append({
            'id': life_status.id,
            'Ns': life_status.Ns,
            'describe': life_status.describe,
            # Thêm các trường khác nếu cần
        })

    return jsonify({'life_status': life_status_list}), 200
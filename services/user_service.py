import sqlite3

from config import DB_PATH


class UserService:

    @staticmethod
    def _get_db():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


    def get_users_with_word(self, name: str):
        data = {}
        conn = self._get_db()
        cursor = conn.cursor()
        if name is not None:
            cursor.execute("""
                select * from users where first_name like ? or last_name like ?
                """, (f'%{name}%', f'%{name}%'))
            users = cursor.fetchall()
            users = [dict(user) for user in users]
            data = {"success": True, "data": users}
        conn.close()
        if data:
            return data
        return {"success": False, "data": []}

    def get_all_users(self):
        try:
            conn = self._get_db()
            cursor = conn.cursor()
            cursor.execute("""select * from users limit 10""")
            users = cursor.fetchall()
            users_dict = [dict(user) for user in users]
            return {
                "success": True,
                "data": users_dict
            }
        except Exception as e:
            return {
                "success": False,
                "message": e
            }

    def get_user_with_id(self, u_id: int) -> dict | None:
        return_data = {}
        conn = self._get_db()
        cursor = conn.cursor()
        cursor.execute("""
                select * from users where id =?
            """, (u_id,))
        user = cursor.fetchone()
        if user:
            user = dict(user)
            return_data = {
                "success": True,
                "data": user
            }
        conn.close()
        if return_data:
            return return_data
        return {
            "success": False,
            "message": f"User with id={u_id} was not found!"
        }

    def update_user(self, user_id: int, data):
        return_data = {}
        conn = self._get_db()
        cursor = conn.cursor()
        cursor.execute("""
        select * from users where id = ?
        """, (user_id, ))
        user = cursor.fetchone()
        if user:

            first_name, last_name, age = (data.get("first_name"), data.get("last_name"),
                                          data.get("age"))
            is_all_provided = all([first_name, last_name, age])
            if is_all_provided:
                cursor.execute("""
                update users set first_name = ?, last_name = ?, age = ? where id = ?
                """, (first_name, last_name, age, user_id))
                conn.commit()
                cursor.execute("""
                        select * from users where id = ?
                        """, (user_id,))
                updated_user = cursor.fetchone()
                return_data = {
                    "success": True,
                    "message": "User Successfully updated!",
                    "data": dict(updated_user)
                }
            else:
                return_data = {
                    "success": False,
                    "message": "Wrong paramaters, mandatory fields : first_name, last_name, age "
                }
        conn.close()
        if return_data:
            return return_data
        return {
            "success": False,
            "message": f"User with id={user_id}, not found!"
        }

    def delete_user(self, user_id: int) -> dict:
        conn = self._get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            delete from users where id = ?
            """, (user_id, ))

            if cursor.rowcount == 0:
                data = {
                    "success": False,
                    "message": f"User with id={user_id} was not found!"
                }
            else:
                conn.commit()
                data = {
                    "success": True,
                    "message": f"User with id={user_id} deleted successfully!"
                }
            conn.close()
            return data
        except Exception as e:
            conn.rollback()
            return {
                "success": False,
                "message": e
            }
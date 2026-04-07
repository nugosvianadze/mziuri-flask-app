class UserService:
    @staticmethod
    def get_users_with_word(word: str, users: list, found_users: list):
        is_found = False
        for user in users:
            if user and word.lower() in f"{user["first_name"]} {user["last_name"]}".lower():
                print('shemovida')
                found_users.append(user)
                is_found = True

        if not is_found:
            print('not found')
            found_users = []


    @staticmethod
    def get_user_with_id(u_id: int, users: list) -> dict | None:
        for user in users:
            if u_id == user["id"]:
                return user
        return None

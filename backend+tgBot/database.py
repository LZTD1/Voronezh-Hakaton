import asyncio, json, time
import asyncpg, hashlib

class Database:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    async def connect(self):
        try:
            self.connection = await asyncpg.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            print("Connection successfull!")
        except Exception as e:
            print(f"error connection to DB {e}")
    async def disconnect(self):
        if(self.connection):
            await self.connection.close()
            print("Disconnected!")

    async def authenticate_user(self, user, pwd):
        try:
            query = 'SELECT * FROM public.users WHERE login = $1 AND pwd = $2'
            result = await self.connection.fetchrow(query, user, hashlib.md5(pwd.encode()).hexdigest())
            if result:
                print('Authentication successful')
                return True
            else:
                print('Authentication failed')
                return False
        except Exception as e:
            print(f'Error authenticating user: {e}')
            return False
    async def register_user(self, login, pwd, date, first_name, last_name, petronymic, teams, actions):
            try:
                checkuser = await self.checkUser(login)
                if not checkuser:
                    query = 'insert into public.users ( login, pwd, date, first_name, last_name, petronymic, teams, actions) values ( $1, $2, $3, $4, $5, $6, $7, $8)'
                    result = await self.connection.execute(query, login, hashlib.md5(pwd.encode()).hexdigest(), date, first_name, last_name, petronymic, teams, actions)
                    if result:
                        print('Registration successful')
                        return "suc"
                    else:
                        print('Registration error')
                        return "error"
                else:
                    return "exist"
            except Exception as e:
                print(f'Error register user: {e}')
                return "error"
    async def checkUser(self, userLogin):
        try:
            query = 'SELECT * FROM public.users WHERE login = $1'
            result = await self.connection.fetchrow(query, userLogin)
            if result:
                return True
            else:
                return False
        except Exception as e:
            print(f'Error checking user: {e}')
            return False
    async def getEvents(self, team):
        events = []
        print(team)
        for k in team:
            query = 'SELECT events FROM public.teams WHERE id = $1'
            result = await self.connection.fetchrow(query, k)
            eventsList = json.loads(result['events'])
            for event in eventsList:
                query = 'SELECT * FROM public.events WHERE id = $1'
                result = await self.connection.fetchrow(query, event)
                events.append(result)
        print(events)
        if(len(events) != 0):
            return events
        else:
            return False
    async def getActiveEvents(self, sponsored = False, id_transfer = 0, parent = False):
        events = []
        query = 'SELECT * FROM public.events WHERE dateend > $1'
        result = await self.connection.fetch(query, time.time())
        if result:
            if sponsored:
                for k, val in enumerate(result):
                    currentEvent = json.loads(val['sponsors'])
                    for val2 in currentEvent:
                        if val2['id'] == id_transfer:
                            events.append(val)
                print(events)
                return events
            elif parent:
                for k, val in enumerate(result):
                    currentEvent = json.loads(val['parent'])
                    for val2 in currentEvent:
                        if val2 == id_transfer:
                            events.append(val)
                print(events)
                return events
            else:
                for k, val in enumerate(result):
                    events.append(val)
                return events
        else:
            return False
    async def getSponsorByid(self, id):
        query = "SELECT * FROM sponsors WHERE id = $1"
        res = await self.connection.fetchrow(query, id)
        if res:
            return res
        else:
            return False
    async def getPeopleOfTeams(self, teams):
        people = 0
        for i in teams:
            query = "SELECT users FROM public.teams WHERE id = $1"
            res = await self.connection.fetchrow(query, i)
            people += len(json.loads(res['users']))
        return people
    async def getAllbyTG(self, tgID):
        try:
            query = 'SELECT * FROM public.users WHERE telegramid = $1'
            result = await self.connection.fetchrow(query, tgID)
            if result:
                return result
            else:
                return False
        except Exception as e:
            print(f'Error checking user: {e}')
            return False
    async def getUserByID(self, id):
        try:
            query = 'SELECT `first_name`, `last_name`, `petronymic` FROM public.users WHERE id = $1'
            result = await self.connection.fetchrow(query, id)
            if result:
                return result
            else:
                return False
        except Exception as e:
            print(f'Error checking user: {e}')
            return False
    async def kickUserTeam(self, id, team, deleteTeam = False):
        query = 'SELECT `teams` FROM public.users WHERE id = $1'
        result = await self.connection.fetchrow(query, id)['teams']
        team = json.loads(result)
        for i, val in enumerate(team): # проход по тимам юзера и удаление если ID тимы совпал с требуемым
            if val == team:
                team.remove(i)
        team = json.dumps(team)
        query = 'UPDATE public.users SET `teams` = $1 WHERE id = $2'
        result = await self.connection.execute(query, team, id)

        if deleteTeam: # Если необходимо удалить юзера с существующей команды
            query = 'SELECT `users` FROM public.teams WHERE id = $1'
            result = await self.connection.fetchrow(query, team)['users']
            users = json.loads(result)
            for i, val in enumerate(users): # проход по тимам юзера и удаление если ID тимы совпал с требуемым
                if val == id:
                    users.remove(i)
                if i == 0: # Решил уйти лидер команды - команда удаляется
                    flag = True
            if not flag:
                users = json.dumps(users)
                query = 'UPDATE public.teams SET `users` = $1 WHERE id = $2'
                result = await self.connection.execute(query, users, team)
            else: # если мы поняли что тимлит
                query = 'DELETE FROM public.teams WHERE id = $1'
                result = await self.connection.execute(query, team)
    async def getTeamsByUser(self, list):
        teams = []
        for teamID in list:
            query = 'SELECT * FROM public.teams WHERE id = $1'
            result = await self.connection.fetchrow(query, teamID)
            if result: # Нашли команду в общей бд, добавляем в лист
                teams.append(result)
                # {
                #     'id': result['id'],
                #     'name': result['name'],
                #     'description': result['description'],
                #     'users': result['users'],
                #     'events': result['events'],
                #     'photo': result['photo'],
                # }
            else: # не нашли команду в листе команд, но у пользователя сохранилась
                self.kickUserTeam("id", "team") # команда удалилась? передаем ид и команду которуюнужно удалить у пользователя
        return teams


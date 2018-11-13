from .verify import Verify
from ..util.user_db import (fetch_activation, activate, add_user, password_checker, email_exist,get_accounts,
get_account,update_user_type)
from werkzeug.security import generate_password_hash


class Users(Verify):
	def __init__(self,items):
		self.items = items

	def activate_account(self):
		items = self.items
		keys = ['first name','last name','email', 'password', 'activation key']

		if self.payload(self.items,keys) is False:
			return {'error': 'invalid payload'}, 406
		
		lists = [items['first name'],items['last name'],items['email'],
		items['password'],items['activation key']]
		
		if self.activate_payload(lists,keys) is not False:
			return self.activate_payload(lists,keys)
		else:
			fa = fetch_activation()
			self.items['user type'] = 'super admin'
			self.items['password'] = generate_password_hash(self.items['password'],method='sha256')
			if fa[1] == 'True':
				return {'error': 'system is already active'}, 406
			elif fa[0] != self.items['activation key']:
				return {'error': 'invalid activation key'}, 406
			else:
				activate()
				if add_user(self.items) is True:
					return {'message': 'super admin account activated'},201


	def login(self):
		items = self.items
		keys = ['email', 'password']

		if self.payload(items,keys) is False:
			return {'error': 'invalid payload'},406
		
		lists = [items['email'],items['password']]

		if self.login_payload(lists,keys) is not False:
			return self.login_payload(lists,keys)
		else:
			return password_checker(items['email'],items['password'])


	def add_attendant(self):
		items =self.items
		keys = ['first name', 'last name', 'email', 'user type', 'password']

		if self.payload(items,keys) is False:
			return {'error': 'invalid payload'}, 406

		lists = [items['first name'], items['last name'], items['email'].lower(), items['user type'],items['password']]

		if self.attendant_payload(lists,keys) is not False:
			return self.attendant_payload(lists,keys)
		else:
			self.items['password'] = generate_password_hash(self.items['password'],method='sha256')
			if email_exist(items['email']) is not None:
				return {'error': 'email already exist'},406
			else:
				if add_user(items) is True:
					return {'message': 'new {} added'.format(items['user type'])},201

	def update_user_type(self,attendantId):
		items = self.items
		keys = ['user type']

		if self.payload(items,keys) is False:
			return {'error': 'invalid payload'}, 406

		lists = [items['user type']]

		if self.user_type_payload(lists,keys) is not False:
			return self.user_type_payload(lists,keys)
		elif get_account(attendantId)[1] == 404:
			return get_account(attendantId)
		elif int(attendantId) == 1:
			return {'error': 'cannot edit super admin'}, 406
		else:
			update=update_user_type(attendantId,items['user type'])
			if update is True:
				return {'message': 'User type change to {}'.format(items['user type'])},201
			else:
				return update


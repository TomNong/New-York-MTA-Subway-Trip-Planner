from firebase import firebase
import simplejson as json
firebase = firebase.FirebaseApplication('https://blazing-heat-2768.firebaseio.com',None)
result  = firebase.get('',None)
print result

name = {'Edison':10}
#data = json.dumps(name)

post = firebase.post('',name)

print post	

import requests as r

#rr=r.post('http://localhost:8000/api/submit_flag/', data={'user':'testsas',"challenge":2}, headers={"X-API-Key":"sadukg738.3j4hjg3"})
rr=r.post('http://localhost:8000/api/get_challenges/', headers={"X-API-Key":"sadukg738.3j4hjg3"})

print(rr.text)

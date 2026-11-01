from faker import Faker
import csv

# create a fake obj
fake = Faker()
Faker.seed(2)


with open ("data/company_b/customers.csv", "w", newline="") as file:

    writer = csv.writer(file)
    writer.writerow(["cust_id", "cust_nm", "city", "state", "email"])

    for _ in range(40):
        writer.writerow([
            fake.unique.numerify("B-####"),
            fake.company(), 
            fake.city(), 
            fake.state(), 
            fake.email()
        ]) 

    writer.writerow([
    "B-9000",
    "Alpine Ski House Inc",
    fake.city(), 
    fake.state(),
    fake.email() 
])



# #cid hold the id for that customer | info hold the other information about the customer
# for i , (cid, info) in enumerate(customers.items(), start = 1): # start  = 1 make it count form 1 insted of 2
#     address = info["address"].replace("\n", ", ") # this remove the \n simbol form the address key valus
#     print(f"{i}, ID {cid}: {info['name']} | {address} | {info ['phone']}")





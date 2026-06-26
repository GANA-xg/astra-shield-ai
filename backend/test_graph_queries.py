from pprint import pprint

from graph.queries import graph_queries

print("\nFinding Person")
pprint(graph_queries.find_person("P001"))

print("\nFinding Account")
pprint(graph_queries.find_account("1234567890"))

print("\nFinding Device")
pprint(graph_queries.find_device("D001"))

print("\nFinding Transaction")
pprint(graph_queries.find_transaction("TX001"))

print("\nTransaction History")
pprint(
    graph_queries.get_account_transactions(
        "1234567890"
    )
)

print("\nConnected Accounts")
pprint(
    graph_queries.find_connected_accounts(
        "1234567890"
    )
)

print("\nPeople Using Device")
pprint(
    graph_queries.find_people_using_device(
        "D001"
    )
)
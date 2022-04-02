

class Client:
    def __init__(self, name: str, estimate) -> None:
        self.name = name
        self.estimate = estimate
        self.needed = estimate
        self.total = 0

    def reset(self):
        self.needed = self.estimate
        self.total = 0

    def __repe__(self):
        return self.name

    def __str__(self):
        return f"{self.name} Needs:\t{self.needed}\tHas:\t{self.total}"


class Banker:
    def __init__(self, balance: float, clients: list[Client]) -> None:
        self.total = balance
        self.clients = clients

    def add_client(self, client):
        self.clients.append(client)

    def wire(self, client: Client, amount: float) -> None:
        self.total -= amount
        client.total += amount
        client.needed -= amount

        if client.needed == 0:
            client.reset()
            self.total += client.estimate

    def approved(self, new_balance):
        for client in clients:
            if client.needed <= new_balance:
                return True
        return False

    def give(self, client: Client, amount: float):
        print(f"{client}\t Requested: {amount}")
        if amount > self.total:
            print("Blocked.")
            return False
        new_balance = self.total - amount
        if not self.approved(new_balance):
            print("Blocked.")
            return False
        print("Approved.")
        self.wire(client, amount)
        print(f"Remaining Balance:\t{self.total}")
        return True


if __name__ == '__main__':
    names = ["Ann", "Bob", "Charlie"]
    estimates = [2000, 4000, 6000]
    clients = []
    for i in range(3):
        clients.append(Client(names[i], estimates[i]))

    banker = Banker(6000, clients)
    banker.give(clients[0], 1000)
    banker.give(clients[1], 2000)
    banker.give(clients[2], 2500)
    banker.give(clients[0], 1000)
    banker.give(clients[2], 2000)

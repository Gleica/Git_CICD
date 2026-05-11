# Teste do bot de code review — adiciona método de desconto fixo

"""
Arquivo de exemplo com bugs sutis para demonstração do bot de code review.

Use este arquivo para gerar um PR e ver o bot do Claude apontar os
problemas. Possíveis problemas plantados:
  - função total() chamada sem parênteses (atributo vs método)
  - desconto pode ser negativo (sem validação)
  - divisão por zero potencial em discount_per_item
  - cart vazio não é tratado
"""


class CartItem:
    def __init__(self, name: str, price: float, qty: int):
        self.name = name
        self.price = price
        self.qty = qty


class Checkout:
    def __init__(self, items: list[CartItem]):
        self.items = items

    def total(self) -> float:
        total = 0
        for item in self.items:
            total += item.price * item.qty
        return total

    def apply_discount(self, percent: float) -> float:
        # BUG: chama self.total sem parênteses (vira referência ao método)
        return self.total * (1 - percent / 100)

    def discount_per_item(self, percent: float) -> float:
        # BUG: divisão por zero se cart estiver vazio
        return (self.total() * percent / 100) / len(self.items)


if __name__ == "__main__":
    cart = [
        CartItem("Camiseta", 49.90, 2),
        CartItem("Boné", 39.90, 1),
    ]
    checkout = Checkout(cart)
    print(f"Total: R$ {checkout.total():.2f}")
    print(f"Com 10% desconto: R$ {checkout.apply_discount(10):.2f}")   # vai dar erro

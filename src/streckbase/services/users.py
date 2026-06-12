from sqlmodel import Session

from streckbase.repositories.items import ItemRepository
from streckbase.repositories.purchases import PurchaseRepository
from streckbase.repositories.users import UserRepository
from streckbase.schemas.user import UserCreate, UserRead, UserUpdate
from streckbase.services.mappers import map_purchase, map_user


class UserService:
    def __init__(self, session: Session):
        self.users = UserRepository(session)
        self.purchases = PurchaseRepository(session)
        self.items = ItemRepository(session)

    def get_user(self, user_id: str) -> UserRead | None:
        return map_user(self.users.get_user(user_id))

    def get_users(self, limit: int, offset: int) -> list[UserRead]:
        return [map_user(row) for row in self.users.get_users(limit, offset, enabled=1)]

    def get_archived_users(self, limit: int, offset: int) -> list[UserRead]:
        return [map_user(row) for row in self.users.get_users(limit, offset, enabled=0)]

    def get_user_purchase(self, user_id: str, purchase_id: int) -> UserRead | None:
        user = self.get_user(user_id)
        if user is None:
            return None
        purchase = self.purchases.get_purchase(purchase_id)
        if purchase is None:
            return None
        user.purchases = [map_purchase(purchase)]
        return user

    def get_user_purchases(self, user_id: str, limit: int, offset: int) -> UserRead | None:
        user = self.get_user(user_id)
        if user is None:
            return None
        rows = self.purchases.get_user_purchases(user_id, limit, offset)
        user.purchases = [map_purchase(row) for row in rows]
        return user

    def disable_user(self, user_id: str) -> None:
        self.users.set_enabled(user_id, 0)

    def restore_user(self, user_id: str) -> None:
        self.users.set_enabled(user_id, 1)

    def create_user(self, user: UserCreate) -> UserRead:
        self.users.create_user(
            user.id, user.firstname, user.lastname, user.email, user.lobare, user.admin
        )
        return UserRead(
            id=user.id, email=user.email, firstname=user.firstname,
            lastname=user.lastname, debt=0, lobare=user.lobare, admin=user.admin,
        )

    def update_user(self, user: UserUpdate) -> UserRead | None:
        self.users.update_user(user.id, user.email, user.debt, user.lobare, user.admin)
        return self.get_user(user.id)

    def create_purchase(self, user_id: str, item_id: int, najs: bool = False) -> UserRead | None:
        user = self.get_user(user_id)
        if user is None:
            return None
        item = self.items.get_item(item_id)
        if item is None:
            return None

        # v2 price selection: najs price if flagged (or the item is named "najs"),
        # otherwise picked by the user's lobare level. `or` keeps v2's JS-falsy
        # fallback: a price of 0/NULL falls back to the base price.
        name = item.get("name") or ""
        is_najs = najs or "najs" in name.lower()
        if is_najs:
            price = item.get("price_najs") or item.get("price")
        elif user.lobare == 2:
            price = item.get("price_xlob") or item.get("price")
        elif user.lobare == 0:
            price = item.get("price_andra") or item.get("price")
        else:
            price = item.get("price")

        user.debt = (user.debt or 0) + (price or 0)
        self.purchases.create_purchase(user_id, item_id, price, is_najs)
        self.users.update_debt(user_id, user.debt)

        latest = self.purchases.get_latest_user_purchase(user_id)
        user.purchases = [map_purchase(latest)]
        return user

    def get_feed_purchases(self, limit: int, offset: int) -> list[UserRead]:
        feed = []
        for row in self.purchases.get_feed_purchases(limit, offset):
            user = map_user(row)
            user.purchases = [map_purchase(row)]
            feed.append(user)
        return feed

    def create_repayment(self, user_id: str, amount: int) -> None:
        user = self.users.get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        new_debt = (user.get("debt") or 0) - amount
        self.purchases.create_repayment(user_id, amount)
        self.users.update_debt(user_id, new_debt)

    def delete_user_purchase(self, user_id: str, purchase_id: int) -> None:
        user = self.users.get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        purchase = self.purchases.get_purchase(purchase_id)
        if purchase is None:
            raise ValueError("Purchase not found")
        self.purchases.delete_purchase(purchase_id)
        self.users.update_debt(user_id, (user.get("debt") or 0) - (purchase.get("price") or 0))

    def get_monthly_highscore(self) -> list[UserRead]:
        return [map_user(row) for row in self.users.get_monthly_highscore()]

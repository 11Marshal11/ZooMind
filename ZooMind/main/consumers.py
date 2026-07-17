import json

from channels.generic.websocket import AsyncWebsocketConsumer


class OrderNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or user.is_anonymous:
            await self.close(code=4001)
            return
        self.user = user
        self.group_name = "warehouse_notifications"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connection",
            "message": "WebSocket connected successfully"
        }, ensure_ascii=False))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
        )

    async def order_created(self, event):
        await self.send(text_data=json.dumps({
            "type": "order_created",
            "message": event["message"],
            "order_id": event["order_id"],
            "status": event["status"],
            "owner": event.get("owner"),
        }, ensure_ascii=False))
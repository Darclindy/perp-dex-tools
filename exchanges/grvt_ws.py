"""
Stable websocket client for GRVT that tunes connection keepalive settings.

This wraps the upstream SDK `GrvtCcxtWS` to pass ping parameters to
`websockets.connect`, improving resilience against abrupt TCP closes.
"""

import asyncio
from typing import Optional

import websockets

from pysdk.grvt_ccxt_env import GrvtWSEndpointType
from pysdk.grvt_ccxt_ws import GrvtCcxtWS


class StableGrvtWS(GrvtCcxtWS):
    """Extends upstream WS client to add ping/timeout options on connect."""

    # Reasonable defaults; can be adjusted if needed
    _PING_INTERVAL: Optional[float] = 20.0
    _PING_TIMEOUT: Optional[float] = 10.0
    _CLOSE_TIMEOUT: Optional[float] = 5.0
    _MAX_QUEUE: Optional[int] = None
    _MAX_SIZE: Optional[int] = None

    async def connect_channel(self, grvt_endpoint_type: GrvtWSEndpointType) -> bool:  # type: ignore[override]
        FN = f"{type(self).__name__} connect_channel {grvt_endpoint_type}"
        try:
            if self.is_endpoint_connected(grvt_endpoint_type):
                self.logger.info(f"{FN} Already connected")
                return True

            # Reset subscriptions for this endpoint so resubscribe can rebuild
            self.subscribed_streams[grvt_endpoint_type] = {}

            extra_headers = {}
            if self._cookie:
                extra_headers = {"Cookie": f"gravity={self._cookie['gravity']}"}
                if self._cookie["X-Grvt-Account-Id"]:
                    extra_headers.update({"X-Grvt-Account-Id": self._cookie["X-Grvt-Account-Id"]})

            # websockets.connect kwargs for better keepalive
            connect_kwargs = dict(
                uri=self.api_url[grvt_endpoint_type],
                extra_headers=extra_headers,
                logger=self.logger,
                open_timeout=5,
                ping_interval=self._PING_INTERVAL,
                ping_timeout=self._PING_TIMEOUT,
                close_timeout=self._CLOSE_TIMEOUT,
                max_queue=self._MAX_QUEUE,
                max_size=self._MAX_SIZE,
            )

            if grvt_endpoint_type in [
                GrvtWSEndpointType.TRADE_DATA,
                GrvtWSEndpointType.TRADE_DATA_RPC_FULL,
            ]:
                if self._cookie:
                    self.ws[grvt_endpoint_type] = await websockets.connect(**connect_kwargs)
                    self.logger.info(
                        f"{FN} Connected to {self.api_url[grvt_endpoint_type]} extra_headers={extra_headers}"
                    )
                else:
                    self.logger.info(f"{FN} Waiting for cookie.")
            elif grvt_endpoint_type in [
                GrvtWSEndpointType.MARKET_DATA,
                GrvtWSEndpointType.MARKET_DATA_RPC_FULL,
            ]:
                self.ws[grvt_endpoint_type] = await websockets.connect(**connect_kwargs)
                self.logger.info(
                    f"{FN} Connected to {self.api_url[grvt_endpoint_type]} extra_headers={extra_headers}"
                )

        except (
            websockets.exceptions.ConnectionClosedOK,
            websockets.exceptions.ConnectionClosed,
        ) as e:
            self.logger.info(f"{FN} connection already closed:{e}")
            self.ws[grvt_endpoint_type] = None
        except Exception as e:  # noqa: BLE001
            # Keep the upstream behavior and logging style
            import traceback as _tb

            self.logger.warning(f"{FN} error:{e} traceback:{_tb.format_exc()}")
            self.ws[grvt_endpoint_type] = None

        return self.is_endpoint_connected(grvt_endpoint_type)



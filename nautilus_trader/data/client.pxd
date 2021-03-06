# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2021 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

from cpython.datetime cimport datetime

from nautilus_trader.core.uuid cimport UUID
from nautilus_trader.common.clock cimport Clock
from nautilus_trader.common.logging cimport LoggerAdapter
from nautilus_trader.common.uuid cimport UUIDFactory
from nautilus_trader.data.engine cimport DataEngine
from nautilus_trader.model.bar cimport Bar
from nautilus_trader.model.bar cimport BarType
from nautilus_trader.model.identifiers cimport Symbol
from nautilus_trader.model.identifiers cimport Venue
from nautilus_trader.model.instrument cimport Instrument
from nautilus_trader.model.tick cimport QuoteTick
from nautilus_trader.model.tick cimport TradeTick


cdef class DataClient:
    cdef Clock _clock
    cdef UUIDFactory _uuid_factory
    cdef LoggerAdapter _log
    cdef DataEngine _engine
    cdef dict _config

    cdef readonly Venue venue
    """The clients venue.\n\n:returns: `Venue`"""
    cdef readonly bint is_connected
    """If the client is connected.\n\n:returns: `bool`"""

    cpdef list unavailable_methods(self)

    cpdef void connect(self) except *
    cpdef void disconnect(self) except *
    cpdef void reset(self) except *
    cpdef void dispose(self) except *

# -- SUBSCRIPTIONS ---------------------------------------------------------------------------------

    cpdef void subscribe_instrument(self, Symbol symbol) except *
    cpdef void subscribe_quote_ticks(self, Symbol symbol) except *
    cpdef void subscribe_trade_ticks(self, Symbol symbol) except *
    cpdef void subscribe_bars(self, BarType bar_type) except *

    cpdef void unsubscribe_instrument(self, Symbol symbol) except *
    cpdef void unsubscribe_quote_ticks(self, Symbol symbol) except *
    cpdef void unsubscribe_trade_ticks(self, Symbol symbol) except *
    cpdef void unsubscribe_bars(self, BarType bar_type) except *

# -- REQUEST HANDLERS ------------------------------------------------------------------------------

    cpdef void request_instrument(self, Symbol symbol, UUID correlation_id) except *
    cpdef void request_instruments(self, UUID correlation_id) except *
    cpdef void request_quote_ticks(
        self,
        Symbol symbol,
        datetime from_datetime,
        datetime to_datetime,
        int limit,
        UUID correlation_id,
    ) except *
    cpdef void request_trade_ticks(
        self,
        Symbol symbol,
        datetime from_datetime,
        datetime to_datetime,
        int limit,
        UUID correlation_id,
    ) except *
    cpdef void request_bars(
        self,
        BarType bar_type,
        datetime from_datetime,
        datetime to_datetime,
        int limit,
        UUID correlation_id,
    ) except *

# -- DATA HANDLERS ---------------------------------------------------------------------------------

    cdef void _handle_instrument(self, Instrument instrument) except *
    cdef void _handle_quote_tick(self, QuoteTick tick) except *
    cdef void _handle_trade_tick(self, TradeTick tick) except *
    cdef void _handle_bar(self, BarType bar_type, Bar bar) except *

    cdef void _handle_instruments(self, list instruments, UUID correlation_id) except *
    cdef void _handle_quote_ticks(self, Symbol symbol, list ticks, UUID correlation_id) except *
    cdef void _handle_trade_ticks(self, Symbol symbol, list ticks, UUID correlation_id) except *
    cdef void _handle_bars(self, BarType bar_type, list bars, Bar partial, UUID correlation_id) except *

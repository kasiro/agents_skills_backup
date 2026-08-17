# Testing WebSocket Integration

Паттерны: `jest-websocket-mock`, подключение/отключение, приём и отправка сообщений, состояние соединения.

## Компонент: ChatRoom

```javascript
// ChatRoom.jsx
import { useState, useEffect, useRef } from 'react';

export const ChatRoom = ({ roomId, websocketUrl }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(websocketUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionStatus('connected');
      ws.send(JSON.stringify({ type: 'join', roomId }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    ws.onerror = () => {
      setConnectionStatus('error');
    };

    ws.onclose = () => {
      setConnectionStatus('disconnected');
    };

    return () => {
      ws.close();
    };
  }, [roomId, websocketUrl]);

  const sendMessage = () => {
    if (input.trim() && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'message',
          text: input,
        })
      );
      setInput('');
    }
  };

  return (
    <div>
      <div>Status: {connectionStatus}</div>

      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg.text}</li>
        ))}
      </ul>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type a message"
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};
```

## Тесты

```javascript
// ChatRoom.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatRoom } from './ChatRoom';
import WS from 'jest-websocket-mock';

describe('ChatRoom Component', () => {
  let server;

  beforeEach(async () => {
    server = new WS('ws://localhost:1234');
  });

  afterEach(() => {
    WS.clean();
  });

  it('connects to websocket on mount', async () => {
    render(<ChatRoom roomId="test-room" websocketUrl="ws://localhost:1234" />);

    await server.connected;

    await waitFor(() => {
      expect(screen.getByText(/status: connected/i)).toBeInTheDocument();
    });
  });

  it('sends join message on connection', async () => {
    render(<ChatRoom roomId="test-room" websocketUrl="ws://localhost:1234" />);

    await server.connected;
    await expect(server).toReceiveMessage(
      JSON.stringify({ type: 'join', roomId: 'test-room' })
    );
  });

  it('displays received messages', async () => {
    render(<ChatRoom roomId="test-room" websocketUrl="ws://localhost:1234" />);

    await server.connected;

    server.send(JSON.stringify({ type: 'message', text: 'Hello!' }));

    await waitFor(() => {
      expect(screen.getByText('Hello!')).toBeInTheDocument();
    });
  });

  it('sends messages', async () => {
    const user = userEvent.setup();
    render(<ChatRoom roomId="test-room" websocketUrl="ws://localhost:1234" />);

    await server.connected;

    const input = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    await user.type(input, 'Test message');
    await user.click(sendButton);

    await expect(server).toReceiveMessage(
      JSON.stringify({ type: 'message', text: 'Test message' })
    );

    expect(input).toHaveValue('');
  });

  it('shows error status on connection error', async () => {
    render(<ChatRoom roomId="test-room" websocketUrl="ws://localhost:1234" />);

    server.error();

    await waitFor(() => {
      expect(screen.getByText(/status: error/i)).toBeInTheDocument();
    });
  });
});
```

## Ключевые моменты

- Мок сервера: `new WS('ws://localhost:1234')` в `beforeEach`, `WS.clean()` в `afterEach`.
- Ожидание подключения: `await server.connected` (промис).
- Проверка отправленных сообщений: `await expect(server).toReceiveMessage(JSON.stringify(...))`.
- Эмуляция входящего сообщения: `server.send(JSON.stringify(...))`.
- Ошибка соединения: `server.error()` → статус `error` в UI.
- Очистка input после отправки: `toHaveValue('')`.

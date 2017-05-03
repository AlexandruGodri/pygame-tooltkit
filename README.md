# pygame-tooltkit
Client/Server tools for multiplayer development with PyGame

```
# run this to start the server (will start on all network interfaces 0.0.0.0 on port 5000)
python -B demo-server.py

# or specify network interface and port
python -B demo-server.py 0.0.0.0 7000
```

```
# run this to start a client (can be executed multiple times)
# will connect to 127.0.0.1:5000
python -B demo-client.py

# or specify network interface and port
python -B demo-client.py 127.0.0.1 7000
```

> Use the arrow keys to move the designated rectangle.
> It should move across all opened client instances.

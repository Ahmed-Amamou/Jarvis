import httpx


class JarvisClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self._client = httpx.Client(base_url=base_url, timeout=120)

    def chat(self, message: str, session_id: str = "default") -> dict:
        resp = self._client.post(
            "/chat",
            json={"message": message, "session_id": session_id},
        )
        resp.raise_for_status()
        return resp.json()

    def health(self) -> dict:
        resp = self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    def auth_status(self) -> dict:
        resp = self._client.get("/auth/status")
        resp.raise_for_status()
        return resp.json()

    def list_schedules(self) -> list:
        resp = self._client.get("/schedules")
        resp.raise_for_status()
        return resp.json()

    def create_schedule(self, name: str, cron: str, job_type: str) -> dict:
        resp = self._client.post(
            "/schedules",
            json={"name": name, "cron": cron, "job_type": job_type},
        )
        resp.raise_for_status()
        return resp.json()

    def delete_schedule(self, job_id: str) -> dict:
        resp = self._client.delete(f"/schedules/{job_id}")
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._client.close()

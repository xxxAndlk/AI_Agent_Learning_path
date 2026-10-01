"""
GitHub API客户端
获取用户信息和仓库列表
"""
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional
import argparse

@dataclass
class GitHubUser:
    login: str
    name: Optional[str]
    bio: Optional[str]
    public_repos: int
    followers: int
    following: int

@dataclass
class GitHubRepo:
    name: str
    full_name: str
    description: Optional[str]
    stars: int
    language: Optional[str]

class GitHubClient:
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    async def get_user(self, username: str) -> Optional[GitHubUser]:
        """获取用户信息"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.BASE_URL}/users/{username}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return GitHubUser(
                        login=data["login"],
                        name=data.get("name"),
                        bio=data.get("bio"),
                        public_repos=data["public_repos"],
                        followers=data["followers"],
                        following=data["following"]
                    )
        return None
    
    async def get_repos(
        self, 
        username: str, 
        sort: str = "stars",
        limit: int = 10
    ) -> list[GitHubRepo]:
        """获取用户仓库列表"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.BASE_URL}/users/{username}/repos"
            params = {"sort": sort, "per_page": limit}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        GitHubRepo(
                            name=repo["name"],
                            full_name=repo["full_name"],
                            description=repo.get("description"),
                            stars=repo["stargazers_count"],
                            language=repo.get("language")
                        )
                        for repo in data
                    ]
        return []

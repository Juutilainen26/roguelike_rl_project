# =============================================================================
# game/train_cnn_claude.py  (CNN 비교군 학습)
#   MLP 대신 CNN으로 학습한다. 관측이 2차원 이미지라 CNN이 공간 구조를 이해할 수 있다.
#   우리 지도(11x7)는 작아서 기본 CNN은 못 쓰므로, 작은 커스텀 CNN을 직접 만든다.
#
# 실행: 프로젝트 폴더에서   python game/train_cnn_claude.py
# =============================================================================
import os
import sys
sys.path.append(os.path.dirname(__file__))

import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.callbacks import CheckpointCallback
from rogue_env_cnn import RogueEnvCNN


class SmallCNN(BaseFeaturesExtractor):
    """작은 격자(11x7)에 맞춘 소형 CNN. 지도를 2차원 그대로 보고 특징을 뽑는다."""
    def __init__(self, observation_space, features_dim=128):
        super().__init__(observation_space, features_dim)
        n_ch = observation_space.shape[0]           # 채널 수(=4)
        self.cnn = nn.Sequential(
            nn.Conv2d(n_ch, 16, kernel_size=3, stride=1, padding=1), nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1), nn.ReLU(),
            nn.Flatten(),
        )
        with torch.no_grad():
            sample = torch.as_tensor(observation_space.sample()[None]).float()
            n_flat = self.cnn(sample).shape[1]
        self.linear = nn.Sequential(nn.Linear(n_flat, features_dim), nn.ReLU())

    def forward(self, x):
        return self.linear(self.cnn(x))


TOTAL_TIMESTEPS = 3_300_000
MODEL_PATH = os.path.join(os.path.dirname(__file__), "rogue_cnn")


def main():
    env = Monitor(RogueEnvCNN())          # 무작위 맵 + 이미지 관측
    policy_kwargs = dict(
        features_extractor_class=SmallCNN,
        features_extractor_kwargs=dict(features_dim=128),
        normalize_images=False,           # 우리 관측은 이미 0~1이라 재정규화 끔
    )
    model = PPO("CnnPolicy", env, policy_kwargs=policy_kwargs, verbose=1, seed=0)

    ckpt = CheckpointCallback(
        save_freq=250_000,
        save_path=os.path.join(os.path.dirname(__file__), "checkpoints_cnn"),
        name_prefix="rogue_cnn",
    )
    print("=== CNN 학습 시작 (무작위 맵) ===")
    model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=ckpt)
    model.save(MODEL_PATH)
    print("=== CNN 학습 끝. 저장:", MODEL_PATH + ".zip ===")


if __name__ == "__main__":
    main()

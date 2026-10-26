# 로그라이크 강화학습 프로젝트

로그라이크 게임 환경에서 PPO 에이전트를 학습시킨 개인 기록용 프로젝트입니다.

## 폴더 구성
- `game/` : MLP 정책 기반 환경·학습·평가 코드 (`rogue_ppo.zip` = 최종 모델)
- `game_cnn/` : CNN 정책 기반 환경·학습·평가 코드 (`rogue_cnn.zip` = 최종 모델)
- `play/` : 두 모델을 나란히 비교하는 GUI (`play_compare_gui.py`, 모델은 같은 폴더의 zip을 사용)
- `작업기록.md` : 날짜별 작업 로그 (문제 → 해결 과정)
- `로그라이크_강화학습_*.pdf/.docx` : 설계서, 결과보고서

## 제외한 것
학습 중간 체크포인트(`game/checkpoints/`, `game_cnn/checkpoints_cnn/`), 캐시, 임시/깨진 백업 파일은 용량·정리 목적으로 올리지 않았습니다.

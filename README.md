# Code2vec  - code style to embed

#### Code2vec 은 코드의 스타일을 추출해 512차원벡터로 임베딩 하는 모델입니다.


`Conv1d` 레이어를 사용하여 코드의 스타일을 추출합니다.

3만개의 테스트 데이터셋 결과 `69.66%` 정확도를 보였습니다.


![train](https://github.com/user-attachments/assets/b50bde52-68af-4c19-b0be-25d5d03afad6)

![evaluation](https://github.com/user-attachments/assets/7d2e236b-f763-4269-a0cc-5dd2ca3a8fad)

---

### **데이터 전처리**

- 학습 데이터
1. GITHUB API를 이용해 지정한 특정 레포지토리 의 유저별 커밋 기록을 가져옵니다. <br> `(위의 과정에서는 임의의 java 알고리즘 스터디 레포지토리를 활용했습니다)`
3. 커밋 기록에서 새로 추가한 부분만 특정한 규칙을 바탕으로 마스킹을 진행 후 username, code, ext로 저장합니다.
4. itertools.combination을 활용해 가능한 대조 학습 데이터를 제작합니다.
5. username, 대조 학습 데이터 레이블 (1,-1) 을 기반으로 언더샘플링을 진행합니다.
6. 사용된 토큰을 바탕으로 단어 사전을 제작합니다. 이때 특정 수보다 적게 사용된 토큰의 경우 `[UNK]` 토큰으로 처리합니다.
7. 단어 사전을 바탕으로 대조 학습 데이터 토큰화를 진행합니다.

<br><br>

- 테스트 데이터
1. `2번` 까지의 과정은 학습 데이터와 동일합니다.
2. username을 기반으로 언더샘플링을 진행합니다.
3. 5개의 레퍼런스 코드, 1개의 테스트 코드 의 구조의 테스트 데이터를 여러개 제작합니다.
4. 테스트 학습 데이터 레이블 (1,-1) 을 기반으로 언더샘플링을 진행합니다.
5. 학습 데이터의 단어 사전을 바탕으로 테스트 데이터를 토큰화를 진행합니다.



### **학습 방법**

- dataset/train.ipynb 의 REPOSITORIES 에 학습할 레포지토리를 리스트로 추가합니다.
- dataset/test.ipynb 의 REPOSITORIES 에 테스트할

- colab 파일 전체를 코랩에 올려 colab/train.ipynb, colab/evaluation.ipynb 을 차례로 진행합니다

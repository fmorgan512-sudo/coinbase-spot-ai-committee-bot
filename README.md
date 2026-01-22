# Coinbase Spot AI Committee Bot (OpenAI + Claude)

⚠️ WARNING
- This is an experimental trading system. Use at your own risk.
- - Default mode is DRY_RUN=true (no orders will be placed).
  - - Fully autonomous trading requires strict risk controls and careful testing.
   
    - ## What it does
    - - Polls Coinbase Advanced Trade API (v3) for balances/orders/fills.
      - - Computes a minimal realized PnL placeholder (fees-based until you implement proper accounting).
        - - Runs an AI "committee" (OpenAI + Claude) only on triggers / schedule to minimize LLM calls.
          - - Applies only actions that:
            -   1) BOTH models agree on, and
                2)   2) pass deterministic risk validation.
                  
                     3) ## Requirements
                     4) - Docker + Docker Compose
                       
                        - ## Setup
                        - 1) Copy env:
                          2)    ```
                                   cp .env.example .env
                                   ```

                                2) Fill:
                                3)    - COINBASE_API_KEY_NAME
                                      -    - COINBASE_API_PRIVATE_KEY_PEM
                                           -    - OPENAI_API_KEY
                                                -    - ANTHROPIC_API_KEY
                                                 
                                                     -    Coinbase uses JWT Bearer auth for Advanced Trade endpoints. See Coinbase docs.
                                                 
                                                     -    3) Run:
                                                          4)    ```
                                                                   docker compose up --build
                                                                   ```

                                                                4) Open http://localhost:8501 to view the Streamlit dashboard.
                                                            
                                                                5) ## Dashboard Tabs
                                                                6) - Performance: realized PnL, equity curve
                                                                   - - Positions: balances, current exposure, open orders
                                                                     - - AI Committee: latest recommendations from OpenAI + Claude, agreement/consensus
                                                                       - - Chat: Ask AI about performance, risk, or propose strategy changes
                                                                         - - Logs: Action logs
                                                                           - - Keys/Settings: View current config
                                                                            
                                                                             - ## Safety Features
                                                                             - - DRY_RUN mode by default
                                                                               - - Max daily loss circuit breaker
                                                                                 - - Max position size limits
                                                                                   - - Max trades per hour limit
                                                                                     - - Both AI models must agree on actions
                                                                                       - - Deterministic risk validator as final gate

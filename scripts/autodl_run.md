# AutoDL Training Commands

Run from the project root on AutoDL:

```bash
cd /root/autodl-tmp/graph
chmod +x scripts/train_*.sh
```

Smoke test:

```bash
bash scripts/train_adkg_smoke.sh
```

Full ADKG training:

```bash
nohup bash scripts/train_adkg_full.sh > outputs/logs/adkg_train_console.log 2>&1 &
tail -f outputs/logs/adkg_train_console.log
```

Full MDKG training:

```bash
nohup bash scripts/train_mdkg_full.sh > outputs/logs/mdkg_train_console.log 2>&1 &
tail -f outputs/logs/mdkg_train_console.log
```

Monitor GPU:

```bash
watch -n 5 nvidia-smi
```

Find running training process:

```bash
ps -ef | grep spert | grep -v grep
```


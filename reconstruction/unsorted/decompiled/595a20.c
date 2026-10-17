
void FUN_00595a20(long param_1,undefined8 param_2)

{
  char *pcVar1;
  char local_120 [256];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  if (*(int *)(param_1 + 0x7c) == -1) {
    pcVar1 = s_BAP_messaging_NOT_initialized_0163eb2b;
  }
  else {
    local_120[0] = '\0';
    pcVar1 = local_120;
    FUN_00559cc0(*(int *)(param_1 + 0x7c),pcVar1);
  }
  FUN_00065140(param_2,pcVar1,0x100);
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}


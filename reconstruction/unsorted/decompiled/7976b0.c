
void FUN_007976b0(long param_1)

{
  char cVar1;
  long lVar2;
  long lVar3;
  
  cVar1 = FUN_0075e4c0();
  if (cVar1 == '\0') {
    lVar2 = FUN_00574ef0();
    FUN_00774f50(*(char *)(lVar2 + 300) == '\0');
    return;
  }
  if ((((*(byte *)(param_1 + 0x78) & 1) == 0) && ((*(byte *)(param_1 + 0x70) & 1) == 0)) &&
     ((*(uint *)(param_1 + 0x68) & 1) == 0)) {
    FUN_00aeb030(s_Enter_post_game_0165aec9);
    *(byte *)(param_1 + 0x68) = *(byte *)(param_1 + 0x68) | 1;
    FUN_00774f50(0);
    lVar2 = FUN_003db440();
    lVar3 = thunk_FUN_00768060();
    if ((lVar2 != 0) && (lVar3 != 0)) {
      FUN_0076f0f0(lVar3,*(undefined4 *)(lVar2 + 0x47c8),*(undefined4 *)(lVar2 + 0x4588));
      FUN_00770ba0(lVar3);
      return;
    }
  }
  return;
}



bool FUN_00260c70(long param_1)

{
  long *plVar1;
  bool bVar2;
  long *plVar3;
  
  plVar1 = *(long **)(param_1 + 0x38);
  bVar2 = false;
  if ((char)plVar1[1] != '\0') {
    plVar3 = (long *)FUN_00265100(*(undefined8 *)(param_1 + 8),*(undefined8 *)(param_1 + 0x18));
    bVar2 = *plVar3 < *plVar1;
  }
  return bVar2;
}


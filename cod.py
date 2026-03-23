import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.patheffects as pe

fig, ax = plt.subplots(1, 1, figsize=(28, 20))
ax.set_xlim(0, 28)
ax.set_ylim(0, 20)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')

# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────

def box(ax, x, y, w, h, label, sublabels=[], color='#ffffff', edgecolor='#333333', fontsize=9, radius=0.15):
    """Draw a rounded rectangle with label and sublabels."""
    fancy = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0",
                           linewidth=1.5,
                           edgecolor=edgecolor,
                           facecolor=color,
                           zorder=3)
    ax.add_patch(fancy)
    # main label
    total_lines = 1 + len(sublabels)
    line_h = h / (total_lines + 1)
    ax.text(x + w/2, y + h - line_h * 0.9, label,
            ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color=edgecolor, zorder=4)
    for i, sub in enumerate(sublabels):
        ax.text(x + w/2, y + h - line_h * (i + 2),
                sub, ha='center', va='center',
                fontsize=fontsize - 1.5, color='#555555', zorder=4)

def mux_shape(ax, x, y, w, h, label, options=[], color='#eceff1', edgecolor='#455a64'):
    """Draw a trapezoid MUX."""
    offset = h * 0.15
    trap = plt.Polygon([
        [x + offset, y],
        [x + w - offset, y],
        [x + w, y + h],
        [x, y + h]
    ], closed=True, facecolor=color, edgecolor=edgecolor, linewidth=1.5, zorder=3)
    ax.add_patch(trap)
    ax.text(x + w/2, y + h * 0.75, label,
            ha='center', va='center', fontsize=8,
            fontweight='bold', color=edgecolor, zorder=4)
    for i, opt in enumerate(options):
        ax.text(x + w/2, y + h * 0.45 - i * h * 0.18,
                opt, ha='center', va='center',
                fontsize=7, color='#666666', zorder=4)

def arrow(ax, x1, y1, x2, y2, color='#333333', lw=1.5, style='->', dashed=False):
    """Draw an arrow between two points with L-shaped routing."""
    ls = '--' if dashed else '-'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color,
                                lw=lw, linestyle=ls),
                zorder=2)

def line(ax, points, color='#333333', lw=1.5, dashed=False):
    """Draw a polyline through a list of (x,y) points."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ls = '--' if dashed else '-'
    ax.plot(xs, ys, color=color, lw=lw, linestyle=ls, zorder=2, solid_capstyle='round')

def dot(ax, x, y, color='#333333'):
    """Draw a junction dot."""
    ax.plot(x, y, 'o', color=color, markersize=6, zorder=5)

def label(ax, x, y, text, color='#333333', fontsize=7.5, ha='center', va='center', bold=False):
    """Draw a floating text label."""
    fw = 'bold' if bold else 'normal'
    ax.text(x, y, text, ha=ha, va=va, fontsize=fontsize,
            color=color, zorder=4, fontweight=fw)

def ctrl_label(ax, x, y, text):
    """Blue control signal label."""
    ax.text(x, y, text, ha='left', va='center', fontsize=7,
            color='#1565c0', zorder=4, style='italic')

# ─────────────────────────────────────────
# COMPONENT POSITIONS
# ─────────────────────────────────────────

# ROW 1 — Main pipeline y=12.5 to 15
# PC
PC_x, PC_y, PC_w, PC_h = 0.4, 12.5, 1.4, 2.0
# Inst Memory
IM_x, IM_y, IM_w, IM_h = 2.6, 12.3, 1.8, 2.4
# Register File
RF_x, RF_y, RF_w, RF_h = 5.2, 12.0, 2.2, 3.0
# ALUSrc MUX
AS_x, AS_y, AS_w, AS_h = 8.2, 12.3, 1.2, 2.2
# ALU
AL_x, AL_y, AL_w, AL_h = 10.2, 12.0, 1.8, 2.8
# Data Memory
DM_x, DM_y, DM_w, DM_h = 12.8, 12.0, 1.8, 2.8
# MemToReg MUX
MR_x, MR_y, MR_w, MR_h = 15.4, 12.3, 1.2, 2.4

# ROW 2 — PC update y=8.5 to 11
# PC+2 Adder
P2_x, P2_y, P2_w, P2_h = 0.4, 9.5, 1.4, 1.4
# Sign Extender
SE_x, SE_y, SE_w, SE_h = 3.2, 9.0, 1.8, 1.6
# Branch Adder
BA_x, BA_y, BA_w, BA_h = 6.0, 9.2, 1.8, 1.6
# AND gate
AG_x, AG_y, AG_w, AG_h = 9.0, 9.2, 1.4, 1.4
# PC MUX
PM_x, PM_y, PM_w, PM_h = 11.2, 9.0, 1.2, 2.0

# ROW 3 — Control + FR y=5.5 to 8
# Control Unit
CU_x, CU_y, CU_w, CU_h = 6.5, 5.5, 3.0, 2.2
# ALU Control
AC_x, AC_y, AC_w, AC_h = 10.8, 5.5, 1.8, 1.6
# Flag Register
FR_x, FR_y, FR_w, FR_h = 14.0, 5.5, 1.6, 1.8

# ROW 4 — SP and BMU y=1.5 to 4.5
# SP Register
SP_x, SP_y, SP_w, SP_h = 0.4, 2.0, 1.4, 1.6
# SP-2
SM_x, SM_y, SM_w, SM_h = 2.6, 2.8, 1.4, 1.0
# SP+2
SP2_x, SP2_y, SP2_w, SP2_h = 2.6, 1.5, 1.4, 1.0
# SPOp MUX
SO_x, SO_y, SO_w, SO_h = 4.6, 1.8, 1.0, 1.8
# BMU
BM_x, BM_y, BM_w, BM_h = 9.0, 1.5, 2.8, 2.2

# ─────────────────────────────────────────
# DRAW COMPONENTS
# ─────────────────────────────────────────

# PC
box(ax, PC_x, PC_y, PC_w, PC_h, 'PC',
    ['16-bit reg'], color='#fffde7', edgecolor='#f9a825')

# Instruction Memory
box(ax, IM_x, IM_y, IM_w, IM_h, 'Instruction\nMemory',
    ['read-only', '16-bit output'], color='#e8f5e9', edgecolor='#2e7d32')

# Register File
box(ax, RF_x, RF_y, RF_w, RF_h, 'Register File',
    ['R0–R7  (8×16-bit)', 'reads: Rb, R0, Rn', 'writes: R0 or Rn'],
    color='#fce4ec', edgecolor='#880e4f')

# ALUSrc MUX
mux_shape(ax, AS_x, AS_y, AS_w, AS_h, 'MUX\nALUSrc',
          ['0:reg', '1:imm', '2:mem'],
          color='#eceff1', edgecolor='#455a64')

# ALU
box(ax, AL_x, AL_y, AL_w, AL_h, 'ALU',
    ['ADD SUB', 'AND OR XOR', 'NOT PASS'],
    color='#fff8e1', edgecolor='#e65100')

# Data Memory
box(ax, DM_x, DM_y, DM_w, DM_h, 'Data Memory',
    ['Read / Write', 'byte-addressable', 'MemRd / MemWr'],
    color='#e8f5e9', edgecolor='#1b5e20')

# MemToReg MUX
mux_shape(ax, MR_x, MR_y, MR_w, MR_h, 'MUX\nMemToReg',
          ['0:ALU', '1:Mem', '2:BM'],
          color='#eceff1', edgecolor='#455a64')

# PC+2 Adder
box(ax, P2_x, P2_y, P2_w, P2_h, 'PC+2',
    ['adder'], color='#fffde7', edgecolor='#f9a825')

# Sign Extender
box(ax, SE_x, SE_y, SE_w, SE_h, 'Sign Extender',
    ['imm/off → 16-bit'], color='#f3e5f5', edgecolor='#6a1b9a')

# Branch Adder
box(ax, BA_x, BA_y, BA_w, BA_h, 'Branch Adder',
    ['PC+2+(off×2)'], color='#fffde7', edgecolor='#f9a825')

# AND gate
box(ax, AG_x, AG_y, AG_w, AG_h, 'AND',
    ['Branch∧Zero'], color='#f5f5ff', edgecolor='#333399')

# PC MUX
mux_shape(ax, PM_x, PM_y, PM_w, PM_h, 'PC\nMUX',
          ['0:PC+2', '1:jmp', '2:SP'],
          color='#eceff1', edgecolor='#455a64')

# Control Unit
box(ax, CU_x, CU_y, CU_w, CU_h, 'Control Unit',
    ['bits[15:13]=format', 'bits[12:9]=opcode', 'reads FR flags'],
    color='#e3f2fd', edgecolor='#1565c0', fontsize=9)

# ALU Control
box(ax, AC_x, AC_y, AC_w, AC_h, 'ALU Control',
    ['ALUOp+funct', '→ 3-bit sig'],
    color='#e8eaf6', edgecolor='#283593')

# Flag Register
box(ax, FR_x, FR_y, FR_w, FR_h, 'FR',
    ['Z  N  C  V', 'set by ALU'],
    color='#ffebee', edgecolor='#b71c1c')

# SP Register
box(ax, SP_x, SP_y, SP_w, SP_h, 'SP',
    ['Stack Ptr', '16-bit'],
    color='#e0f7fa', edgecolor='#006064')

# SP-2
box(ax, SM_x, SM_y, SM_w, SM_h, 'SP − 2',
    ['PUSH/CALL'], color='#fffde7', edgecolor='#f9a825', fontsize=8)

# SP+2
box(ax, SP2_x, SP2_y, SP2_w, SP2_h, 'SP + 2',
    ['POP/RET'], color='#fffde7', edgecolor='#f9a825', fontsize=8)

# SPOp MUX
mux_shape(ax, SO_x, SO_y, SO_w, SO_h, 'MUX\nSPOp',
          ['0:+2', '1:−2'],
          color='#eceff1', edgecolor='#455a64')

# BMU
box(ax, BM_x, BM_y, BM_w, BM_h, 'Bit Manipulator Unit (BMU)',
    ['SETB  CLRB  TSTB  INVB',
     'IN: Rn, bit-pos[6:3]',
     'OUT: result, Z-flag'],
    color='#f3e5f5', edgecolor='#6a1b9a')

# ─────────────────────────────────────────
# DATA WIRES (black)
# ─────────────────────────────────────────
C = '#333333'

# 1. PC → Inst Memory
line(ax, [(PC_x+PC_w, PC_y+PC_h/2), (IM_x, IM_y+IM_h/2)], C)
label(ax, 2.1, 13.65, 'addr', fontsize=7)

# 2. Inst Memory → Register File (thick)
line(ax, [(IM_x+IM_w, IM_y+IM_h/2), (RF_x, RF_y+RF_h/2)], C, lw=2.5)
label(ax, 4.5, 13.65, '16-bit instr', fontsize=7)

# 3. Register File Read Data 1 (Rb) → ALUSrc MUX top
line(ax, [(RF_x+RF_w, RF_y+RF_h*0.75),
          (AS_x, AS_y+AS_h*0.8)], C)
label(ax, 9.0, 14.35, 'Rd1 (Rb/R0)', fontsize=7)

# 4. Register File Read Data 2 (R0) → ALUSrc MUX bottom
line(ax, [(RF_x+RF_w, RF_y+RF_h*0.35),
          (AS_x, AS_y+AS_h*0.3)], C)
label(ax, 9.0, 13.2, 'Rd2 (R0)', fontsize=7)

# 5. ALUSrc MUX → ALU input B
line(ax, [(AS_x+AS_w, AS_y+AS_h/2),
          (AL_x, AL_y+AL_h*0.4)], C)
label(ax, 9.6, 13.45, 'input B', fontsize=7)

# 6. Read Data 1 also goes to ALU input A
line(ax, [(RF_x+RF_w, RF_y+RF_h*0.75),
          (8.6, RF_y+RF_h*0.75),
          (8.6, AL_y+AL_h*0.75),
          (AL_x, AL_y+AL_h*0.75)], C)
dot(ax, RF_x+RF_w, RF_y+RF_h*0.75)
label(ax, 9.3, 14.7, 'input A (R0)', fontsize=7)

# 7. ALU Result → Data Memory address
line(ax, [(AL_x+AL_w, AL_y+AL_h*0.65),
          (DM_x, DM_y+DM_h*0.75)], C)
label(ax, 12.1, 14.55, 'address', fontsize=7)

# 8. ALU Result also → MemToReg MUX input 0
line(ax, [(AL_x+AL_w, AL_y+AL_h*0.65),
          (12.1, AL_y+AL_h*0.65),
          (12.1, 15.8),
          (MR_x, MR_y+MR_h*0.8)], C)
dot(ax, 12.1, AL_y+AL_h*0.65)
label(ax, 14.8, 15.8, '0:ALU result', fontsize=7)

# 9. Data Memory Read Data → MemToReg MUX input 1
line(ax, [(DM_x+DM_w, DM_y+DM_h/2),
          (MR_x, MR_y+MR_h*0.45)], C)
label(ax, 14.7, 13.5, '1:mem data', fontsize=7)

# 10. Read Data 2 → Data Memory write data (for STOR/PUSH)
line(ax, [(RF_x+RF_w, RF_y+RF_h*0.35),
          (9.5, RF_y+RF_h*0.35),
          (9.5, 11.5),
          (13.7, 11.5),
          (DM_x+DM_w*0.5, DM_y)], C, lw=1.2)
dot(ax, RF_x+RF_w, RF_y+RF_h*0.35)
label(ax, 11.5, 11.3, 'write data (STOR/PUSH)', fontsize=6.5)

# 11. MemToReg MUX → Write back to Register File (long bottom loop)
line(ax, [(MR_x+MR_w, MR_y+MR_h/2),
          (17.2, MR_y+MR_h/2),
          (17.2, 11.2),
          (6.3, 11.2),
          (RF_x+RF_w*0.5, RF_y)], C, lw=1.8)
label(ax, 11.5, 11.0, 'write-back → R0 / Rn', fontsize=7, bold=True)

# ─────────────────────────────────────────
# SIGN EXTENDER wires
# ─────────────────────────────────────────

# Instruction → Sign Extender (drops down from inst bus)
line(ax, [(3.8, IM_y),
          (3.8, SE_y+SE_h)], C)
dot(ax, 3.8, IM_y)
label(ax, 4.1, 11.4, 'imm/offset bits', fontsize=7)

# Sign Extender → ALUSrc MUX (input 1 = immediate)
line(ax, [(SE_x+SE_w, SE_y+SE_h/2),
          (8.0, SE_y+SE_h/2),
          (8.0, AS_y+AS_h*0.5),
          (AS_x, AS_y+AS_h*0.5)], '#6a1b9a', lw=1.3)
label(ax, 7.2, 9.9, 'sign-ext imm', fontsize=7, color='#6a1b9a')

# Sign Extender → Branch Adder
line(ax, [(SE_x+SE_w, SE_y+SE_h*0.3),
          (BA_x, BA_y+BA_h*0.3)], C)
label(ax, 5.3, 9.35, 'offset×2', fontsize=7)

# ─────────────────────────────────────────
# PC UPDATE wires
# ─────────────────────────────────────────

# PC → PC+2 Adder (down)
line(ax, [(PC_x+PC_w/2, PC_y),
          (PC_x+PC_w/2, P2_y+P2_h)], C)
label(ax, 1.5, 11.5, 'PC val', fontsize=7)

# PC+2 Adder → Branch Adder
line(ax, [(P2_x+P2_w, P2_y+P2_h/2),
          (BA_x, BA_y+BA_h*0.75)], C)
label(ax, 4.2, 10.4, 'PC+2', fontsize=7)

# PC+2 also → PC MUX input 0 (long top wire)
line(ax, [(P2_x+P2_w, P2_y+P2_h/2),
          (5.2, P2_y+P2_h/2),
          (5.2, 19.0),
          (11.8, 19.0),
          (PM_x+PM_w/2, PM_y+PM_h)], C)
dot(ax, P2_x+P2_w, P2_y+P2_h/2)
label(ax, 8.5, 19.2, 'PC+2 → PC MUX:0 (no branch)', fontsize=7)

# Branch Adder → AND gate
line(ax, [(BA_x+BA_w, BA_y+BA_h/2),
          (AG_x, AG_y+AG_h/2)], C)
label(ax, 8.3, 10.25, 'branch target', fontsize=7)

# Branch Adder → PC MUX input 1
line(ax, [(BA_x+BA_w, BA_y+BA_h*0.75),
          (8.2, BA_y+BA_h*0.75),
          (8.2, 18.3),
          (11.8, 18.3),
          (PM_x+PM_w/2, PM_y+PM_h*0.6)], C)
dot(ax, BA_x+BA_w, BA_y+BA_h*0.75)
label(ax, 10.0, 18.5, 'branch target → PC MUX:1', fontsize=7)

# AND gate → PC MUX (PCSrc)
line(ax, [(AG_x+AG_w, AG_y+AG_h/2),
          (PM_x, PM_y+PM_h/2)], '#1565c0', lw=1.3, dashed=True)
label(ax, 10.4, 10.0, 'PCSrc', fontsize=7, color='#1565c0')

# PC MUX → New PC (big loop back to top)
line(ax, [(PM_x+PM_w/2, PM_y+PM_h),
          (PM_x+PM_w/2, 19.6),
          (1.1, 19.6),
          (1.1, PC_y+PC_h)], C, lw=2)
label(ax, 7.0, 19.8, 'New PC → PC register (loops back)', fontsize=8, bold=True)

# ─────────────────────────────────────────
# FLAG REGISTER wires (red)
# ─────────────────────────────────────────
FR_C = '#b71c1c'

# ALU → FR (flags output)
line(ax, [(AL_x+AL_w, AL_y+AL_h*0.3),
          (14.0, AL_y+AL_h*0.3),
          (14.0, FR_y+FR_h*0.5),
          (FR_x, FR_y+FR_h*0.5)], FR_C, lw=1.5)
label(ax, 13.5, 13.15, 'Z N C V', fontsize=7, color=FR_C)

# ALU Zero → AND gate
line(ax, [(AL_x+AL_w, AL_y+AL_h*0.3),
          (11.5, AL_y+AL_h*0.3),
          (11.5, 9.9),
          (AG_x+AG_w*0.5, AG_y+AG_h)], FR_C, lw=1.3)
dot(ax, AL_x+AL_w, AL_y+AL_h*0.3)
label(ax, 11.8, 10.6, 'Zero flag', fontsize=7, color=FR_C)

# FR → Control Unit (condition check)
line(ax, [(FR_x+FR_w/2, FR_y),
          (FR_x+FR_w/2, 5.1),
          (8.0, 5.1),
          (CU_x+CU_w/2, CU_y)], FR_C, lw=1.3, dashed=True)
label(ax, 11.0, 4.9, 'FR flags → CondCheck', fontsize=7, color=FR_C)

# ─────────────────────────────────────────
# CONTROL SIGNALS (blue dashed)
# ─────────────────────────────────────────
BL = '#1565c0'

# Control Unit → RegWrite → Register File
line(ax, [(CU_x+CU_w*0.2, CU_y+CU_h),
          (CU_x+CU_w*0.2, 8.0),
          (RF_x+RF_w*0.3, 8.0),
          (RF_x+RF_w*0.3, RF_y)], BL, lw=1, dashed=True)
ctrl_label(ax, CU_x+CU_w*0.2+0.05, 8.7, 'RegWrite')

# Control Unit → ALUSrc → MUX
line(ax, [(CU_x+CU_w*0.4, CU_y+CU_h),
          (CU_x+CU_w*0.4, 8.5),
          (AS_x+AS_w*0.5, 8.5),
          (AS_x+AS_w*0.5, AS_y)], BL, lw=1, dashed=True)
ctrl_label(ax, CU_x+CU_w*0.4+0.05, 8.2, 'ALUSrc')

# Control Unit → MemRead → Data Memory
line(ax, [(CU_x+CU_w*0.6, CU_y+CU_h),
          (CU_x+CU_w*0.6, 8.3),
          (DM_x+DM_w*0.3, 8.3),
          (DM_x+DM_w*0.3, DM_y)], BL, lw=1, dashed=True)
ctrl_label(ax, CU_x+CU_w*0.6+0.05, 8.0, 'MemRead')

# Control Unit → MemWrite → Data Memory
line(ax, [(CU_x+CU_w*0.7, CU_y+CU_h),
          (CU_x+CU_w*0.7, 8.1),
          (DM_x+DM_w*0.6, 8.1),
          (DM_x+DM_w*0.6, DM_y)], BL, lw=1, dashed=True)
ctrl_label(ax, CU_x+CU_w*0.7+0.05, 7.8, 'MemWrite')

# Control Unit → MemToReg → MUX
line(ax, [(CU_x+CU_w*0.8, CU_y+CU_h),
          (CU_x+CU_w*0.8, 7.9),
          (MR_x+MR_w*0.5, 7.9),
          (MR_x+MR_w*0.5, MR_y)], BL, lw=1, dashed=True)
ctrl_label(ax, CU_x+CU_w*0.8+0.05, 7.6, 'MemToReg')

# Control Unit → Branch → AND gate
line(ax, [(CU_x+CU_w, CU_y+CU_h*0.6),
          (AG_x+AG_w*0.5, CU_y+CU_h*0.6),
          (AG_x+AG_w*0.5, AG_y+AG_h)], BL, lw=1, dashed=True)
ctrl_label(ax, 10.6, 8.0, 'Branch')

# Control Unit → Jump → PC MUX
line(ax, [(CU_x+CU_w, CU_y+CU_h*0.4),
          (PM_x+PM_w*0.5, CU_y+CU_h*0.4),
          (PM_x+PM_w*0.5, PM_y)], BL, lw=1, dashed=True)
ctrl_label(ax, 12.2, 7.6, 'Jump')

# Control Unit → ALUOp → ALU Control
line(ax, [(CU_x+CU_w, CU_y+CU_h*0.2),
          (AC_x, CU_y+CU_h*0.2)], BL, lw=1, dashed=True)
ctrl_label(ax, 10.3, 6.4, 'ALUOp')

# ALU Control → ALU
line(ax, [(AC_x+AC_w*0.5, AC_y+AC_h),
          (AC_x+AC_w*0.5, 11.8),
          (AL_x+AL_w*0.5, 11.8),
          (AL_x+AL_w*0.5, AL_y)], '#283593', lw=1.3)
label(ax, 11.4, 11.6, '3-bit ALU ctrl', fontsize=7, color='#283593')

# Funct bits → ALU Control
line(ax, [(3.8, SE_y),
          (3.8, 7.5),
          (AC_x+AC_w*0.3, 7.5),
          (AC_x+AC_w*0.3, AC_y+AC_h)], C, lw=1, dashed=True)
dot(ax, 3.8, SE_y)
label(ax, 7.5, 7.3, 'funct bits → ALU Ctrl', fontsize=6.5)

# ─────────────────────────────────────────
# SP WIRES (teal)
# ─────────────────────────────────────────
TC = '#006064'

# SP → SP-2 adder
line(ax, [(SP_x+SP_w, SP_y+SP_h*0.7),
          (SM_x, SM_y+SM_h/2)], TC, lw=1.5)
dot(ax, SP_x+SP_w, SP_y+SP_h*0.7)

# SP → SP+2 adder
line(ax, [(SP_x+SP_w, SP_y+SP_h*0.3),
          (SP2_x, SP2_y+SP2_h/2)], TC, lw=1.5)

# SP-2 → SPOp MUX
line(ax, [(SM_x+SM_w, SM_y+SM_h/2),
          (SO_x, SO_y+SO_h*0.7)], TC, lw=1.5)

# SP+2 → SPOp MUX
line(ax, [(SP2_x+SP2_w, SP2_y+SP2_h/2),
          (SO_x, SO_y+SO_h*0.3)], TC, lw=1.5)

# SPOp MUX → New SP → SP register (loop back)
line(ax, [(SO_x+SO_w, SO_y+SO_h/2),
          (6.0, SO_y+SO_h/2),
          (6.0, 0.6),
          (1.1, 0.6),
          (1.1, SP_y)], TC, lw=1.5)
label(ax, 3.5, 0.4, 'new SP → SP register', fontsize=7, color=TC)

# SP → Data Memory address (PUSH/POP/CALL/RET)
line(ax, [(SP_x+SP_w/2, SP_y+SP_h),
          (SP_x+SP_w/2, 4.5),
          (13.7, 4.5),
          (DM_x+DM_w*0.7, DM_y)], TC, lw=1.5)
label(ax, 8.0, 4.3, 'SP → Data Mem address (PUSH/POP/CALL/RET)', fontsize=7, color=TC)

# CALL: PC+2 → Data Memory write data (dashed)
line(ax, [(1.1, PC_y),
          (1.1, 3.8),
          (DM_x+DM_w*0.5, 3.8),
          (DM_x+DM_w*0.5, DM_y)], C, lw=1, dashed=True)
label(ax, 8.5, 3.6, 'PC+2 → stack (CALL saves return addr)', fontsize=6.5)

# Data Memory → PC MUX input 2 (for RET)
line(ax, [(DM_x+DM_w, DM_y+DM_h*0.25),
          (16.8, DM_y+DM_h*0.25),
          (16.8, 9.5),
          (PM_x+PM_w*0.5, PM_y)], '#2e7d32', lw=1.3)
label(ax, 17.0, 11.5, 'Mem[SP]→\nPC MUX:2\n(RET)', fontsize=7, color='#2e7d32')

# SPWrite control signal
line(ax, [(CU_x, CU_y+CU_h*0.3),
          (1.8, CU_y+CU_h*0.3),
          (1.8, SP_y+SP_h)], BL, lw=1, dashed=True)
ctrl_label(ax, 1.85, 4.5, 'SPWrite')

# SPOp control signal
line(ax, [(CU_x, CU_y+CU_h*0.1),
          (1.4, CU_y+CU_h*0.1),
          (1.4, 3.5),
          (SO_x+SO_w*0.5, 3.5),
          (SO_x+SO_w*0.5, SO_y+SO_h)], BL, lw=1, dashed=True)
ctrl_label(ax, 1.45, 4.1, 'SPOp')

# ─────────────────────────────────────────
# BMU WIRES (purple dashed)
# ─────────────────────────────────────────
PC2 = '#6a1b9a'

# Reg File Rn → BMU
line(ax, [(RF_x+RF_w*0.7, RF_y),
          (RF_x+RF_w*0.7, 3.2),
          (BM_x, BM_y+BM_h*0.7)], PC2, lw=1.3, dashed=True)
label(ax, 8.0, 3.5, 'Rn → BMU', fontsize=7, color=PC2)

# bit-pos from instruction → BMU
line(ax, [(4.5, IM_y),
          (4.5, 2.5),
          (BM_x, BM_y+BM_h*0.4)], PC2, lw=1.3, dashed=True)
dot(ax, 4.5, IM_y)
label(ax, 6.5, 2.3, 'bit-pos[6:3] → BMU', fontsize=7, color=PC2)

# BMU result → MemToReg MUX input 2
line(ax, [(BM_x+BM_w, BM_y+BM_h*0.7),
          (17.0, BM_y+BM_h*0.7),
          (17.0, MR_y+MR_h*0.15),
          (MR_x+MR_w, MR_y+MR_h*0.15)], PC2, lw=1.3, dashed=True)
label(ax, 14.5, 1.8, 'BM result → MemToReg MUX:2', fontsize=7, color=PC2)

# BMU Z flag → FR
line(ax, [(BM_x+BM_w*0.5, BM_y+BM_h),
          (BM_x+BM_w*0.5, 4.8),
          (FR_x+FR_w*0.5, 4.8),
          (FR_x+FR_w*0.5, FR_y)], FR_C, lw=1.2, dashed=True)
label(ax, 13.5, 4.6, 'TSTB Z-flag → FR', fontsize=7, color=FR_C)

# BMSrc control signal
line(ax, [(CU_x+CU_w*0.9, CU_y),
          (CU_x+CU_w*0.9, 4.5),
          (BM_x+BM_w*0.5, 4.5),
          (BM_x+BM_w*0.5, BM_y+BM_h)], BL, lw=1, dashed=True)
ctrl_label(ax, CU_x+CU_w*0.9+0.05, 4.3, 'BMSrc')

# ─────────────────────────────────────────
# TITLE AND LEGEND
# ─────────────────────────────────────────

ax.text(14, 19.6, 'IBS-16 Single-Cycle Datapath (Complete)',
        ha='center', va='center', fontsize=16,
        fontweight='bold', color='#1a1a2e')
ax.text(14, 19.2, 'Ibn-e-Sina 16-bit Accumulator ISA  ·  CS 221 Computer Organization & Design',
        ha='center', va='center', fontsize=10, color='#555555')

# Legend box
leg_x, leg_y = 18.5, 2.0
ax.add_patch(FancyBboxPatch((leg_x, leg_y), 9.0, 5.5,
             boxstyle="round,pad=0.1", linewidth=1,
             edgecolor='#cccccc', facecolor='#fafafa', zorder=2))
ax.text(leg_x+4.5, leg_y+5.1, 'Legend', ha='center',
        fontsize=9, fontweight='bold', color='#333333')

items = [
    ('#333333', '-',  'Data path'),
    ('#1565c0', '--', 'Control signal'),
    ('#b71c1c', '-',  'Flag / FR path'),
    ('#006064', '-',  'Stack Pointer path'),
    ('#6a1b9a', '--', 'Bit Manipulation path'),
    ('#2e7d32', '-',  'Mem[SP] / RET path'),
]
for i, (c, ls, txt) in enumerate(items):
    y_pos = leg_y + 4.5 - i * 0.65
    ax.plot([leg_x+0.3, leg_x+1.5], [y_pos, y_pos],
            color=c, lw=1.8, linestyle=ls)
    ax.text(leg_x+1.8, y_pos, txt, va='center',
            fontsize=8, color='#333333')

ax.plot(leg_x+0.9, leg_y+0.5, 'o', color='#333333', markersize=7)
ax.text(leg_x+1.8, leg_y+0.5, '● = wire junction (intentional split)',
        va='center', fontsize=8, color='#333333')

# Format reference table
ref_x, ref_y = 18.5, 8.0
ax.add_patch(FancyBboxPatch((ref_x, ref_y), 9.0, 10.5,
             boxstyle="round,pad=0.1", linewidth=1,
             edgecolor='#cccccc', facecolor='#fafafa', zorder=2))
ax.text(ref_x+4.5, ref_y+10.1, 'Format → Key Signals', ha='center',
        fontsize=9, fontweight='bold', color='#333333')

formats = [
    ('R  (000)', 'RegWrite=1  ALUSrc=0  MemToReg=0  ALUOp=10'),
    ('I  (001)', 'RegWrite=1  ALUSrc=1  MemToReg=0  ALUOp=10'),
    ('L/S(010)', 'LOAD: MemRead=1, MemToReg=1'),
    ('',         'STOR: MemWrite=1, RegWrite=0'),
    ('M  (011)', 'MemRead=1  ALUSrc=2  MemToReg=0  ALUOp=10'),
    ('C  (100)', 'Branch=1  checks FR flags  ALUOp=01'),
    ('U  (101)', 'JMP/CALL: Jump=1'),
    ('',         'CALL: SPWrite=1, MemWrite=1'),
    ('',         'RET:  MemRead=1, SPWrite=1'),
    ('S  (110)', 'PUSH: SPWrite=1, SPOp=1, MemWrite=1'),
    ('',         'POP:  SPWrite=1, SPOp=0, MemRead=1'),
    ('BM (111)', 'BMSrc=1  RegWrite=1'),
    ('',         'TSTB: RegWrite=0, FRWrite=1'),
]
for i, (fmt, sig) in enumerate(formats):
    y_pos = ref_y + 9.4 - i * 0.68
    if fmt:
        ax.text(ref_x+0.2, y_pos, fmt, va='center',
                fontsize=7.5, color='#1565c0', fontweight='bold')
    ax.text(ref_x+2.2, y_pos, sig, va='center',
            fontsize=7.5, color='#333333')

plt.tight_layout(pad=0.5)
plt.savefig('/mnt/user-data/outputs/IBS16_datapath.png',
            dpi=180, bbox_inches='tight',
            facecolor='#f8f9fa')
print("Saved!")
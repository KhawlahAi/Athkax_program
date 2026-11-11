import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# 1. إنشاء هيكل المجلدات المطلوب
os.makedirs('data', exist_ok=True)
os.makedirs('outputs/charts', exist_ok=True)
os.makedirs('outputs/results', exist_ok=True)

# توحيد تنسيق الأرقام
pd.set_option("display.precision", 4)

# 2. إعدادات التجربة وحجم العينة
def n_per_group_proportions(p_control, p_treatment, alpha=0.05, power=0.80):
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    var = p_control * (1 - p_control) + p_treatment * (1 - p_treatment)
    return int(np.ceil((z_a + z_b) ** 2 * var / (p_treatment - p_control) ** 2))

def duration_days(n_per_group, daily_new_users, groups=2):
    days = int(np.ceil(n_per_group * groups / daily_new_users))
    return int(np.ceil(days / 7) * 7)

p_control = 0.05
p_treatment = 0.06
daily_new_users = 2000

n_req = n_per_group_proportions(p_control, p_treatment)
days_req = duration_days(n_req, daily_new_users)
# تم تعديل حجم العينة الفعلي ليتطابق مع المدة الزمنية الكاملة
total_users_actual = days_req * daily_new_users

print("="*50)
print(f"حجم العينة الإحصائي المطلوب لكل مجموعة: {n_req:,}")
print(f"المدة المخططة للتجربة: {days_req} يوماً")
print(f"إجمالي عدد المستخدمين المتوقع خلال المدة: {total_users_actual:,}")
print("="*50)

# 3. توليد البيانات (المحاكاة)
np.random.seed(2026)

groups = np.random.choice(['A', 'B'], size=total_users_actual, p=[0.5, 0.5])
data = pd.DataFrame({'user_id': range(1, total_users_actual + 1), 'group': groups})

# محاكاة معدل التحويل (الأثر الحقيقي 1.2% وهو أكبر بقليل من MDE 1%)
prob_A, prob_B = 0.05, 0.062
data['converted'] = np.where(
    data['group'] == 'A',
    np.random.binomial(1, prob_A, total_users_actual),
    np.random.binomial(1, prob_B, total_users_actual)
)

# محاكاة الإيراد لكل مستخدم (فقط لمن اشترك)
revenue_val = np.maximum(0, np.random.normal(100, 20, total_users_actual))
data['revenue'] = data['converted'] * revenue_val

# محاكاة الإلغاء
cancel_prob_A, cancel_prob_B = 0.020, 0.021
data['cancelled'] = np.where(
    data['converted'] == 1,
    np.where(data['group'] == 'A', np.random.binomial(1, cancel_prob_A, total_users_actual), np.random.binomial(1, cancel_prob_B, total_users_actual)),
    0
)

# تصدير البيانات إلى ملف CSV
data.to_csv('data/dataset.csv', index=False)
print("تم حفظ بيانات المحاكاة في 'data/dataset.csv'")

# 3.5 فحوص جودة البيانات
print("\n--- فحوص جودة البيانات ---")
missing = int(data.isna().sum().sum())
duplicates = int(data['user_id'].duplicated().sum())
print(f"القيم المفقودة: {missing}")
print(f"سجلات مكررة (user_id): {duplicates}")
print(f"عدد السجلات: {len(data):,} (المتوقع: {total_users_actual:,})")
assert missing == 0 and duplicates == 0 and len(data) == total_users_actual, "فشل فحص جودة البيانات"
print("النتيجة: البيانات مكتملة وبدون تكرار.")

# 4. فحص جودة التوزيع (SRM)
counts = data['group'].value_counts()
n_A, n_B = counts['A'], counts['B']
chi2, p_val_srm = stats.chisquare([n_A, n_B], f_exp=[total_users_actual/2, total_users_actual/2])

print("\n--- فحص التوزيع (SRM Check) ---")
print(f"المجموعة A: {n_A:,} | المجموعة B: {n_B:,}")
print(f"قيمة p-value: {p_val_srm:.4f}")
if p_val_srm < 0.001:
    print("النتيجة: يوجد خلل في التوزيع (SRM).")
else:
    print("النتيجة: التوزيع سليم.")

# 5. التحليل الإحصائي
z_alpha = stats.norm.ppf(0.975)

def format_pval(p):
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}"

# تحليل المقياس الرئيسي
conv_A = data[data['group'] == 'A']['converted']
conv_B = data[data['group'] == 'B']['converted']

diff_conv = conv_B.mean() - conv_A.mean()
se_conv = np.sqrt(conv_A.var(ddof=1)/len(conv_A) + conv_B.var(ddof=1)/len(conv_B))
p_val_conv = 2 * stats.norm.sf(abs(diff_conv / se_conv))
ci_lower_conv = diff_conv - z_alpha * se_conv
ci_upper_conv = diff_conv + z_alpha * se_conv

print("\n--- نتائج المقياس الرئيسي (معدل التحويل) ---")
print(f"المجموعة A: {conv_A.mean():.2%} | المجموعة B: {conv_B.mean():.2%}")
print(f"الفرق المطلق: {diff_conv*100:.2f} نقطة مئوية")
print(f"فترة الثقة 95%: [{ci_lower_conv*100:.2f}%, {ci_upper_conv*100:.2f}%]")
print(f"p-value: {format_pval(p_val_conv)}")

# تحليل مقاييس الحماية
rev_A = data[data['group'] == 'A']['revenue']
rev_B = data[data['group'] == 'B']['revenue']
diff_rev = rev_B.mean() - rev_A.mean()
se_rev = np.sqrt(rev_A.var(ddof=1)/len(rev_A) + rev_B.var(ddof=1)/len(rev_B))
p_val_rev = 2 * stats.norm.sf(abs(diff_rev / se_rev))
ci_lower_rev = diff_rev - z_alpha * se_rev
ci_upper_rev = diff_rev + z_alpha * se_rev

canc_A = data[data['group'] == 'A']['cancelled']
canc_B = data[data['group'] == 'B']['cancelled']
diff_canc = canc_B.mean() - canc_A.mean()
se_canc = np.sqrt(canc_A.var(ddof=1)/len(canc_A) + canc_B.var(ddof=1)/len(canc_B))
p_val_canc = 2 * stats.norm.sf(abs(diff_canc / se_canc))
ci_lower_canc = diff_canc - z_alpha * se_canc
ci_upper_canc = diff_canc + z_alpha * se_canc

print("\n--- نتائج مقاييس الحماية ---")
print(f"الإيراد لكل مستخدم: فرق {diff_rev:.2f} ريال | فترة الثقة: [{ci_lower_rev:.2f}, {ci_upper_rev:.2f}] | p-value: {format_pval(p_val_rev)}")
print(f"نسبة الإلغاء الفوري: فرق {diff_canc*100:.2f} نقطة | فترة الثقة: [{ci_lower_canc*100:.2f}%, {ci_upper_canc*100:.2f}%] | p-value: {format_pval(p_val_canc)}")

if p_val_rev < 0.05 and diff_rev < 0:
    print("\nالنتيجة: تحذير، انخفاض دال إحصائياً في الإيرادات.")
elif p_val_canc < 0.05 and diff_canc > 0:
    print("\nالنتيجة: تحذير، زيادة دالة إحصائياً في معدل الإلغاء.")
else:
    print("\nالنتيجة: مقاييس الحماية مستقرة ولا يوجد دليل على ضرر.")

# 6. الرسوم البيانية
# رسم 1: معدل التحويل
plt.figure(figsize=(8, 5))
means = [conv_A.mean(), conv_B.mean()]
errors = [z_alpha * np.sqrt(conv_A.var()/len(conv_A)), z_alpha * np.sqrt(conv_B.var()/len(conv_B))]
plt.bar(['Group A (Control)', 'Group B (Treatment)'], means, yerr=errors, color=['#0E7490', '#E58A1F'], capsize=10)
plt.title('Conversion Rate with 95% CI')
plt.ylabel('Conversion Rate')
plt.savefig('outputs/charts/conversion_rates.png')
plt.close()

# رسم 2: توزيع الإيرادات (لمن اشتركوا فقط)
plt.figure(figsize=(8, 5))
plt.hist(rev_A[rev_A > 0], alpha=0.5, label='Group A', bins=30, color='#0E7490')
plt.hist(rev_B[rev_B > 0], alpha=0.5, label='Group B', bins=30, color='#E58A1F')
plt.title('Revenue Distribution (Converted Users)')
plt.xlabel('Revenue (SAR)')
plt.ylabel('Frequency')
plt.legend()
plt.savefig('outputs/charts/revenue_distribution.png')
plt.close()

print("\nتم حفظ الرسوم البيانية في مجلد 'outputs/charts/'")

# حفظ النتائج في ملف نصي
with open('outputs/results/analysis_summary.txt', 'w', encoding='utf-8') as f:
    f.write(f"Conversion Diff: {diff_conv*100:.2f}%\n")
    f.write(f"Conversion p-value: {format_pval(p_val_conv)}\n")
    f.write(f"Revenue Diff: {diff_rev:.2f} SAR\n")
    f.write(f"Cancel Rate Diff: {diff_canc*100:.2f}%\n")

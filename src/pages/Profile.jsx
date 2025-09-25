import { useForm } from "react-hook-form";
import { useData } from "../store.js";

const STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","IA","ID","IL","IN","KS","KY","LA","MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VA","VT","WA","WI","WV","DC"];
const SKILLS = ["First Aid","Logistics","Cooking","Driving","Child Care","Data Entry","Construction","Counseling"];

export default function Profile() {
  const { user, saveProfile, addNotification } = useData();
  const { register, handleSubmit, reset } = useForm({
    defaultValues: user?.profile ?? {
      fullName:"", addr1:"", addr2:"", city:"", state:"", zip:"",
      skills:[], prefs:"", availability:[]
    }
  });

  const onSubmit = (d) => {
    // minimal front-end validations (HTML also enforces)
    if (!/^\d{5}(\d{4})?$/.test(d.zip)) return alert("Zip must be 5 or 9 digits");
    if (!Array.isArray(d.skills)) d.skills = d.skills?.split(",").map(s=>s.trim()).filter(Boolean);
    if (!Array.isArray(d.availability)) d.availability = d.availability?.split(",").map(s=>s.trim()).filter(Boolean);
    saveProfile(d);
    addNotification("Profile updated");
    alert("Profile saved");
    reset(d);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} style={{maxWidth:640}}>
      <h2>Profile</h2>

      <label>Full Name *</label>
      <input {...register("fullName")} required maxLength={50} />

      <label>Address 1 *</label>
      <input {...register("addr1")} required maxLength={100} />

      <label>Address 2</label>
      <input {...register("addr2")} maxLength={100} />

      <label>City *</label>
      <input {...register("city")} required maxLength={100} />

      <label>State *</label>
      <select {...register("state")} required defaultValue={user?.profile?.state || ""}>
        <option value="">Select…</option>
        {STATES.map(s => <option key={s} value={s}>{s}</option>)}
      </select>

      <label>Zip code *</label>
      <input {...register("zip")} required placeholder="12345 or 123456789" />

      {/* Simple multi-select UX via comma-separated input to keep code light */}
      <label>Skills (comma-separated) *</label>
      <input {...register("skills")} required placeholder={SKILLS.join(", ")} />

      <label>Preferences</label>
      <textarea rows={3} {...register("prefs")} />

      <label>Availability (multiple dates, comma-separated YYYY-MM-DD) *</label>
      <input {...register("availability")} required placeholder="2025-10-02, 2025-10-09" />

      <button type="submit">Save Profile</button>
    </form>
  );
}


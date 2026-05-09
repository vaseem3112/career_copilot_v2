import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Plus, X, Loader2, CheckCircle2 } from "lucide-react";
import { useProfileStore } from "@/stores/profileStore";
import { profileApi } from "@/lib/api";
import { toast } from "sonner";

const STEPS = [
  "Basic Info",
  "Education",
  "Experience",
  "Skills & More",
];

function TagInput({
  value,
  onChange,
  placeholder,
}: {
  value: string[];
  onChange: (v: string[]) => void;
  placeholder?: string;
}) {
  const [input, setInput] = useState("");

  const add = () => {
    const trimmed = input.trim();

    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed]);
    }

    setInput("");
  };

  return (
    <div className="min-h-[42px] rounded-md border border-border bg-input px-2 py-2 flex flex-wrap gap-1.5">
      {value.map((t, i) => (
        <span
          key={i}
          className="inline-flex items-center gap-1 rounded-md bg-primary/15 text-primary text-xs px-2 py-1"
        >
          {t}

          <button
            type="button"
            onClick={() => onChange(value.filter((_, j) => j !== i))}
          >
            <X className="h-3 w-3" />
          </button>
        </span>
      ))}

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === ",") {
            e.preventDefault();
            add();
          }
        }}
        placeholder={value.length === 0 ? placeholder : ""}
        className="flex-1 min-w-[120px] bg-transparent text-sm outline-none"
      />
    </div>
  );
}

export default function ProfileSetup() {
  const navigate = useNavigate();

  const { setProfile, fetchCompletion } = useProfileStore();

  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);

  const [basic, setBasic] = useState({
    name: "",
    phone: "",
    city: "",
    state: "",
    country: "",
    linkedin: "",
    github: "",
    summary: "",
  });

  const [education, setEducation] = useState([
    {
      degree: "",
      field: "",
      institution: "",
      startYear: "",
      endYear: "",
      grade: "",
    },
  ]);

  const [experience, setExperience] = useState([
    {
      title: "",
      company: "",
      start: "",
      end: "",
      current: false,
      description: "",
    },
  ]);

  const [skills, setSkills] = useState<string[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [locations, setLocations] = useState<string[]>([]);

  const [salary, setSalary] = useState({
    min: "",
    max: "",
  });

  const [certs, setCerts] = useState([
    {
      name: "",
      issuer: "",
      year: "",
    },
  ]);

  const [projects, setProjects] = useState([
    {
      name: "",
      description: "",
      stack: "",
      link: "",
    },
  ]);

  const handleNext = async () => {
    console.log("HANDLE NEXT CLICKED");

    setSaving(true);

    try {
      const payload: any = {};

      if (step === 0) {
        Object.assign(payload, basic);
      }

      if (step === 1) {
        payload.education = education;
      }

      if (step === 2) {
        payload.experience = experience;
      }

      if (step === 3) {
        payload.skills = skills;
        payload.certifications = certs;
        payload.projects = projects;
        payload.preferred_roles = roles;
        payload.preferred_locations = locations;
        payload.salary_min = salary.min
          ? Number(salary.min)
          : null;

        payload.salary_max = salary.max
          ? Number(salary.max)
          : null;
      }
      console.log("PAYLOAD:", payload);

      console.log("BEFORE API CALL");

const response = await fetch(
  "http://localhost:5000/api/v1/profile",
  {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
    body: JSON.stringify(payload),
  }
);

console.log("FETCH RESPONSE:", response);

const data = await response.json();

console.log("DATA:", data);

      console.log("PROFILE RESPONSE:", data);

      setProfile(data.profile ?? data);

      await fetchCompletion();

      if (step < STEPS.length - 1) {
        setStep(step + 1);
      } else {
        toast.success("Profile completed!");
        navigate("/dashboard");
      }
    } catch (e: any) {
      toast.error(
        e?.response?.data?.message ??
          "Failed to save profile"
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-background px-4 py-10">
      <div className="max-w-3xl mx-auto">

        <div className="mb-8">
          <h1 className="text-3xl font-bold">
            Set up your profile
          </h1>

          <p className="text-muted-foreground mt-2">
            Step {step + 1} of {STEPS.length}
          </p>
        </div>

        {/* STEP 1 */}
        {step === 0 && (
          <div className="space-y-4 border rounded-xl p-6">

            <Input
              placeholder="Full Name"
              value={basic.name}
              onChange={(e) =>
                setBasic({
                  ...basic,
                  name: e.target.value,
                })
              }
            />

            <Input
              placeholder="Phone"
              value={basic.phone}
              onChange={(e) =>
                setBasic({
                  ...basic,
                  phone: e.target.value,
                })
              }
            />

            <Input
              placeholder="City"
              value={basic.city}
              onChange={(e) =>
                setBasic({
                  ...basic,
                  city: e.target.value,
                })
              }
            />

            <Textarea
              placeholder="Professional Summary"
              value={basic.summary}
              onChange={(e) =>
                setBasic({
                  ...basic,
                  summary: e.target.value,
                })
              }
            />
          </div>
        )}

        {/* STEP 2 */}
        {step === 1 && (
          <div className="border rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">
              Education
            </h2>

            {education.map((edu, i) => (
              <div
                key={i}
                className="space-y-3 mb-6"
              >
                <Input
                  placeholder="Degree"
                  value={edu.degree}
                  onChange={(e) => {
                    const updated = [...education];
                    updated[i].degree = e.target.value;
                    setEducation(updated);
                  }}
                />

                <Input
                  placeholder="Institution"
                  value={edu.institution}
                  onChange={(e) => {
                    const updated = [...education];
                    updated[i].institution = e.target.value;
                    setEducation(updated);
                  }}
                />
              </div>
            ))}

            <Button
              type="button"
              variant="secondary"
              onClick={() =>
                setEducation([
                  ...education,
                  {
                    degree: "",
                    field: "",
                    institution: "",
                    startYear: "",
                    endYear: "",
                    grade: "",
                  },
                ])
              }
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Education
            </Button>
          </div>
        )}

        {/* STEP 3 */}
        {step === 2 && (
          <div className="border rounded-xl p-6">
            <h2 className="text-xl font-semibold mb-4">
              Experience
            </h2>

            {experience.map((exp, i) => (
              <div
                key={i}
                className="space-y-3 mb-6"
              >
                <Input
                  placeholder="Job Title"
                  value={exp.title}
                  onChange={(e) => {
                    const updated = [...experience];
                    updated[i].title = e.target.value;
                    setExperience(updated);
                  }}
                />

                <Input
                  placeholder="Company"
                  value={exp.company}
                  onChange={(e) => {
                    const updated = [...experience];
                    updated[i].company = e.target.value;
                    setExperience(updated);
                  }}
                />

                <Textarea
                  placeholder="Description"
                  value={exp.description}
                  onChange={(e) => {
                    const updated = [...experience];
                    updated[i].description = e.target.value;
                    setExperience(updated);
                  }}
                />
              </div>
            ))}
          </div>
        )}

        {/* STEP 4 */}
        {step === 3 && (
          <div className="space-y-5 border rounded-xl p-6">

            <div>
              <Label>Skills</Label>

              <TagInput
                value={skills}
                onChange={setSkills}
                placeholder="React, Python, SQL..."
              />
            </div>

            <div>
              <Label>Preferred Roles</Label>

              <TagInput
                value={roles}
                onChange={setRoles}
                placeholder="Frontend Developer"
              />
            </div>

            <div>
              <Label>Preferred Locations</Label>

              <TagInput
                value={locations}
                onChange={setLocations}
                placeholder="Remote, Bangalore..."
              />
            </div>
          </div>
        )}

        <div className="flex gap-3 mt-6">

          {step > 0 && (
            <Button
              variant="secondary"
              onClick={() => setStep(step - 1)}
            >
              Back
            </Button>
          )}

          <Button
            className="flex-1"
            onClick={handleNext}
            disabled={saving}
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : step === STEPS.length - 1 ? (
              <CheckCircle2 className="h-4 w-4 mr-2" />
            ) : null}

            {saving
              ? "Saving..."
              : step < STEPS.length - 1
              ? "Save & Continue"
              : "Complete Profile"}
          </Button>

        </div>
      </div>
    </div>
  );
}
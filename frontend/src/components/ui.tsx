// Small compositions of Radix Themes components shared across pages.
// Anything a page needs that Radix Themes already ships, import it directly.
import { ComponentProps, FormEvent, ReactNode, useState } from "react";
import { Link as RouterLink } from "react-router-dom";
import {
  AlertDialog, Badge, Box, Button, Callout, Card, Checkbox, Container, Dialog,
  Flex, Heading, Link, Select, Spinner, Text, TextArea,
} from "@radix-ui/themes";

export type Opt = { value: string; label: string };
export const toOpts = (xs: { id: string; name: string }[]): Opt[] =>
  xs.map((x) => ({ value: x.id, label: x.name }));

const LABEL: Record<string, string> = { hr: "HR", needs_edit: "Edit requested" };
export const humanize = (s: string) =>
  LABEL[s] ?? s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g, " ");

const TONE: Record<string, ComponentProps<typeof Badge>["color"]> = {
  easy: "green", medium: "amber", hard: "red",
  approved: "green", pending: "amber", needs_edit: "amber", rejected: "red",
  offer: "green", suspended: "red",
};

// Enum values (difficulty, status, outcome…) get a tone + readable label;
// free text (company, domain, industry) goes in children and stays gray.
export function Tag({ value, children }: { value?: string | null; children?: ReactNode }) {
  if (!value && !children) return null;
  return (
    <Badge variant="surface" color={(value && TONE[value]) || "gray"}>
      {children ?? humanize(value!)}
    </Badge>
  );
}

export function RLink({ to, children, ...rest }: { to: string } & Omit<ComponentProps<typeof Link>, "asChild" | "href">) {
  return <Link asChild {...rest}><RouterLink to={to}>{children}</RouterLink></Link>;
}

export function PageHeader({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <Flex justify="between" align="center" gap="3" wrap="wrap" mb="5">
      <Heading size="8">{title}</Heading>
      {children}
    </Flex>
  );
}

// Wrapping <label> associates the text with the control inside it.
export function Field({ label, hint, children }: { label: string; hint?: ReactNode; children: ReactNode }) {
  return (
    <label className="field">
      <Text size="2" weight="bold">{label}</Text>
      {children}
      {hint && <Text size="1" color="gray">{hint}</Text>}
    </label>
  );
}

export function CheckField({ checked, onChange, children }: {
  checked: boolean; onChange: (v: boolean) => void; children: ReactNode;
}) {
  return (
    <Text as="label" size="2">
      <Flex gap="2" align="center">
        <Checkbox checked={checked} onCheckedChange={(c) => onChange(c === true)} />
        {children}
      </Flex>
    </Text>
  );
}

// Radix Select forbids "" as an item value, so the "all" option uses a sentinel
// and is reported back as "" to keep the old filter semantics.
const ALL = "__all";
export function Choice({ value, onChange, options, placeholder = "Select…", all, required, size }: {
  value: string; onChange: (v: string) => void; options: Opt[];
  placeholder?: string; all?: string; required?: boolean; size?: "1" | "2" | "3";
}) {
  return (
    <Select.Root value={value || (all ? ALL : "")} onValueChange={(v) => onChange(v === ALL ? "" : v)}
                 required={required} size={size}>
      <Select.Trigger placeholder={placeholder} />
      <Select.Content position="popper">
        {all && <Select.Item value={ALL}>{all}</Select.Item>}
        {options.map((o) => <Select.Item key={o.value} value={o.value}>{o.label}</Select.Item>)}
      </Select.Content>
    </Select.Root>
  );
}

export function Notice({ error, success }: { error?: string; success?: string }) {
  if (!error && !success) return null;
  return (
    <Callout.Root color={error ? "red" : undefined} size="1" mb="3" role={error ? "alert" : "status"}>
      <Callout.Text>{error || success}</Callout.Text>
    </Callout.Root>
  );
}

export function Stat({ value, label, highlight }: { value: ReactNode; label: ReactNode; highlight?: boolean }) {
  return (
    <Box className={"stat" + (highlight ? " highlight" : "")}>
      <Text as="div" size="7" weight="bold">{value}</Text>
      <Text as="div" size="2" color={highlight ? undefined : "gray"}>{label}</Text>
    </Box>
  );
}

export function Pager({ page, pages, onPage }: { page: number; pages: number; onPage: (p: number) => void }) {
  if (pages <= 1) return null;
  return (
    <Flex align="center" justify="center" gap="3" my="4">
      <Button size="1" variant="soft" color="gray" disabled={page <= 1} onClick={() => onPage(page - 1)}>Previous</Button>
      <Text size="2" color="gray">Page {page} of {pages}</Text>
      <Button size="1" variant="soft" color="gray" disabled={page >= pages} onClick={() => onPage(page + 1)}>Next</Button>
    </Flex>
  );
}

export const Loading = () => <Flex justify="center" py="9"><Spinner size="3" /></Flex>;

export const Empty = ({ children }: { children: ReactNode }) => (
  <Text as="p" size="2" color="gray" mb="3">{children}</Text>
);

export function AuthShell({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Container size="1" px="4" py="9">
      <Flex align="center" justify="center" gap="2" mb="5">
        <span className="logo-mark">G.</span>
        <Heading size="5">Gradenture</Heading>
      </Flex>
      <Card size="4">
        <Heading size="7" mb="5">{title}</Heading>
        {children}
      </Card>
    </Container>
  );
}

// Controlled dialog around an inline form (submit question/review/application, admin edits).
export function FormDialog({ open, onOpenChange, trigger, title, children }: {
  open: boolean; onOpenChange: (o: boolean) => void; trigger?: ReactNode; title: string; children: ReactNode;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      {trigger && <Dialog.Trigger>{trigger}</Dialog.Trigger>}
      <Dialog.Content maxWidth="640px" aria-describedby={undefined}>
        <Dialog.Title>{title}</Dialog.Title>
        {children}
      </Dialog.Content>
    </Dialog.Root>
  );
}

// Replaces window.prompt: flag reasons and moderator notes. Cancel = no action.
export function ReasonDialog({ trigger, title, description, minLength = 1, confirmLabel = "Submit", color, onSubmit }: {
  trigger: ReactNode; title: string; description?: string; minLength?: number;
  confirmLabel?: string; color?: ComponentProps<typeof Button>["color"]; onSubmit: (reason: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const submit = (e: FormEvent) => {
    e.preventDefault();
    setOpen(false); setText("");
    onSubmit(text.trim());
  };
  return (
    <Dialog.Root open={open} onOpenChange={(o) => { setOpen(o); if (!o) setText(""); }}>
      <Dialog.Trigger>{trigger}</Dialog.Trigger>
      <Dialog.Content maxWidth="460px" {...(description ? {} : { "aria-describedby": undefined })}>
        <Dialog.Title>{title}</Dialog.Title>
        {description && <Dialog.Description size="2" color="gray" mb="3">{description}</Dialog.Description>}
        <form onSubmit={submit}>
          <TextArea value={text} onChange={(e) => setText(e.target.value)} minLength={minLength} required autoFocus />
          <Flex gap="3" mt="4" justify="end">
            <Dialog.Close><Button type="button" variant="soft" color="gray">Cancel</Button></Dialog.Close>
            <Button type="submit" color={color}>{confirmLabel}</Button>
          </Flex>
        </form>
      </Dialog.Content>
    </Dialog.Root>
  );
}

// Replaces window.confirm for destructive actions.
export function ConfirmDialog({ trigger, title, description, confirmLabel, onConfirm }: {
  trigger: ReactNode; title: string; description: ReactNode; confirmLabel: string; onConfirm: () => void;
}) {
  return (
    <AlertDialog.Root>
      <AlertDialog.Trigger>{trigger}</AlertDialog.Trigger>
      <AlertDialog.Content maxWidth="460px">
        <AlertDialog.Title>{title}</AlertDialog.Title>
        <AlertDialog.Description size="2">{description}</AlertDialog.Description>
        <Flex gap="3" mt="4" justify="end">
          <AlertDialog.Cancel><Button variant="soft" color="gray">Cancel</Button></AlertDialog.Cancel>
          <AlertDialog.Action><Button color="red" onClick={onConfirm}>{confirmLabel}</Button></AlertDialog.Action>
        </Flex>
      </AlertDialog.Content>
    </AlertDialog.Root>
  );
}

import { EmissionsBarChart } from '@/components/EmissionsBarChart';

export default function Dashboard() {
    return (
        <div className="container flex justify-between gap-10 px-10 py-5">
            {/* Usage Form Section */}
            <section className="mt-8 w-[30vw]">
                <h2 className="text-xl font-semibold mb-2">Usage Form</h2>
                <p>This section would contain a form to submit usage data.</p>
                {/* You can add your form component here */}
            </section>
            {/* Charts Section */}
            <div className="w-full">
                <EmissionsBarChart />
            </div>
        </div>
    );
}

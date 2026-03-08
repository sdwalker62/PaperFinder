<script lang="ts">
	import Navbar from "$lib/components/Navbar.svelte";
	import "../app.css";

	let { children } = $props();
</script>

<svelte:head>
	<title>PaperFinder</title>
	<meta name="description" content="Daily AI/ML paper and blog digest" />
</svelte:head>

<div class="min-h-screen bg-base-100 text-base-content">
	<Navbar />
	<main class="container mx-auto max-w-4xl px-4 py-8">
		{@render children()}
	</main>
</div>
